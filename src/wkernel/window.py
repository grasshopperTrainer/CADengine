import threading
import time
import glfw

from numbers import Number

from wkernel.devices.bits import DrawInterface
from ckernel.context_tree import ContextManager
from .glyph import GlyphNode, GlyphInterface
from .devices.master import DeviceMaster
from global_tools.callback_registry import callbackRegistry
from global_tools import FPSTimer


class Window(DrawInterface, GlyphInterface):
    """
    Class for baking exact instance that's on screen

    """

    def __init__(self, width, height, name, monitor=None, shared=None, **kwargs):
        super().__init__()
        # in case shared window exists, need to get context from it
        self.__context = ContextManager(width, height, name, monitor, shared, window=self)
        self.__name = name

        with self.__context.gl as gl:
            gl.glEnable(gl.GL_SCISSOR_TEST)
            gl.glEnable(gl.GL_DEPTH_TEST)
            gl.glDepthFunc(gl.GL_LESS)

            gl.glEnable(gl.GL_BLEND)
            gl.glBlendEquation(gl.GL_FUNC_ADD)
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

            gl.glEnable(gl.GL_PROGRAM_POINT_SIZE)

            gl.glEnable(gl.GL_PRIMITIVE_RESTART_FIXED_INDEX)

            # glfw.swap_interval(1)

        with self.__context.glfw as glfw_window:
            glfw.set_window_close_callback(glfw_window, self.__close_window)
            glfw.set_input_mode(self.context.glfw_window, glfw.STICKY_MOUSE_BUTTONS, glfw.TRUE)

        # make view object
        self.__glyph = GlyphNode(0, 0, width, height, None, None, None, None)

        self._render_thread = threading.Thread(target=self.__run, name=name)
        self._pipelines = []

        self.__fps = 30
        self.__timer = FPSTimer(self.__fps)
        self.__num_draw_frame = None
        self.__frame_count = 0

        self.__device_manager = DeviceMaster(self)

        self.__flag_indraw = False

    def __str__(self):
        return f"<Window: {self.__name}>"
    @property
    def glyph(self) -> GlyphNode:
        """
        implementation of abstract method
        :return:
        """
        return self.__glyph

    @property
    def devices(self) -> DeviceMaster:
        """
        return DeviceManager which handles keyboard and mouse operation

        :return:
        """
        return self.__device_manager

    @property
    def fps(self):
        """
        window render frame rate per sec

        :return:
        """
        return self.__fps

    @property
    def context(self):
        """
        read only

        :return:
        """
        return self.__context

    @fps.setter
    def fps(self, per_sec):
        """
        set frame rate per second
        
        :param per_sec: Number
        :return: 
        """
        if not isinstance(per_sec, Number):
            raise TypeError
        self.__fps = per_sec
        self.__timer.tfps = per_sec

    @property
    def is_drawing(self):
        return self.__flag_indraw

    def append_pipeline(self, pipeline):
        self._pipelines.append(pipeline)

    def __run(self):
        """
        Rendering thread incuding operations per-frame

        :return:
        """
        # bind and as this is a drawing happends in dedicated thread no need to unbind
        with self.__context.glfw as glfw_window:
            while not glfw.window_should_close(glfw_window):
                if self.__frame_count == self.__num_draw_frame:
                    break  # if number of drawn frame is targeted number of frame drawn
                with self.__timer:  # __exit__ of timer will hold thread by time.sleep()
                    with self.__context.gl:
                        self.call_predraw_callback()
                        self.__flag_indraw = True
                        self.draw()
                        self.__flag_indraw = False
                        self.call_postdraw_callback()
                        glfw.swap_buffers(glfw_window)
                self.__frame_count += 1

    def __close_window(self, window):
        """
        if not joined, glfw function can be called where there is no glfw context
        anymore. Downside of joining is that window destruction will only occur
        when draw waiting is over - meaning destruction only takes place after a frame
        this can cause 'noticable stall' when fps is very low

        to detour this problem, window is hidden before actually being destroyed
        :param window:
        :return:
        """
        with self.__context.glfw as window:
            glfw.hide_window(window)  # <- glfw window still alive here
            self._render_thread.join()
            self.__context.context_master.remove_window(self)
            glfw.destroy_window(window)  # <- window destoied here

    def set_num_draw_frame(self, num):
        """
        set number of frame to draw

        Window will stall after drawing given number of frames.

        :param num: int number of frames to draw
        :return:
        """
        if not isinstance(num, (type(None), int)):
            raise TypeError
        self.__num_draw_frame = num

    def run_all(self, num_draw_frame=None):
        """
        Main function running all application

        :param num_draw_frame: int number of frames to draw
        :return:
        """
        for window in self.__context.context_master.iter_all_windows():
            window.set_num_draw_frame(num_draw_frame)
            window._render_thread.start()
        # main thread. all function calls that has to work in full speed should be here
        while self.__context.context_master.has_window():
            with self.__timer:
                self.__context.context_master.glfw.poll_events()
        self.__context.context_master.glfw.terminate()  # no window alive means end of opengl functionality

    def draw(self):
        """
        glfw, OpenGL placeholder to be overridden by the user

        this method is called with OpenGL binding. OpenGL function calls can be dealt unless another OpenGL context is
        bound within this draw call.

        :return:
        """

    def setup(self):
        pass

    @callbackRegistry
    def call_predraw_callback(self):
        """
        called befor draw function
        :return:
        """
        pass

    @call_predraw_callback.appender
    def append_predraw_callback(self, func, *args, **kwargs):
        pass

    @callbackRegistry
    def call_postdraw_callback(self):
        """
        called after draw function
        :return:
        """
        pass

    @call_postdraw_callback.appender
    def append_postdraw_callback(self, func, *args, **kwargs):
        pass


if __name__ == '__main__':
    window1 = Window(400, 400, 'main window')
    window2 = Window(500, 500, 'second')
    Window.run_all()
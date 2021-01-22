import threading
import time

from numbers import Number

from wkernel.devices.bits import DrawInterface
from ckernel.context_nodes import ContextManager
from .glyph import GlyphNode, GlyphInterface
from .devices.master import DeviceMaster
from global_tools.callback_registry import callbackRegistry


class Timer:
    """
    Time recorder for maintaining given fps
    """

    def __init__(self, target_fps):
        self._marked_time = 0
        self._tfps = target_fps  # target frame per second
        self._dtpf = 1 / target_fps # delay time per frame

    def __enter__(self):
        self._marked_time = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        loop_duration = time.time() - self._marked_time
        wait = self._dtpf - loop_duration
        if wait >= 0:
            time.sleep(wait)

    @property
    def tfps(self):
        return self._tfps

    @tfps.setter
    def tfps(self, v):
        self._tfps = v
        self._dtpf = 1 / self._tfps


class Window(DrawInterface, GlyphInterface):
    """
    Class for baking exact instance that's on screen

    """

    def __init__(self, width, height, name, monitor=None, shared=None, **kwargs):
        super().__init__()
        # in case shared window exists, need to get context from it
        if shared is not None and isinstance(shared, Window):
            self.__context = shared.get_context()
        else:
            self.__context = ContextManager(width, height, name, monitor, shared, window=self)

        with self.__context.gl as gl:
            gl.glEnable(gl.GL_SCISSOR_TEST)
            gl.glEnable(gl.GL_DEPTH_TEST)
            gl.glDepthFunc(gl.GL_LESS)

            gl.glEnable(gl.GL_BLEND)
            gl.glBlendEquation(gl.GL_FUNC_ADD)
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

            gl.glEnable(gl.GL_PROGRAM_POINT_SIZE)
        with self.__context.glfw as glfw:
            glfw.set_window_close_callback(self.__close_window)

        # make view object
        self.__glyph = GlyphNode(0, 0, width, height, None, None, None, None)

        self._render_thread = threading.Thread(target=self.__run)
        self._pipelines = []

        self.__frame_rate = 30
        self.__timer = Timer(self.__frame_rate)
        self.__num_draw_frame = None
        self.__frame_count = 0

        # default camera
        # FIXME: this is bad bad
        self.__device_manager = DeviceMaster(self)
        self.devices.cameras[0].body.builder.in3_aspect_ratio = self.devices.panes[0].glyph.aspect_ratio

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
    def framerate(self):
        """
        window render frame rate per sec

        :return:
        """
        return self.__frame_rate

    @property
    def context(self):
        """
        read only

        :return:
        """
        return self.__context

    @framerate.setter
    def framerate(self, per_sec):
        """
        set frame rate per second
        
        :param per_sec: Number
        :return: 
        """
        if not isinstance(per_sec, Number):
            raise TypeError
        self.__frame_rate = per_sec
        self.__timer.tfps = per_sec

    def append_pipeline(self, pipeline):
        self._pipelines.append(pipeline)

    def __run(self):
        """
        Rendering thread incuding operations per-frame

        :return:
        """
        # bind and as this is a rendering happends in dedicated thread no need to unbind
        with self.__context.glfw as glfw:
            while not glfw.window_should_close():
                if self.__frame_count == self.__num_draw_frame:
                    break  # if number of drawn frame is targeted number of frame drawn
                with self.__timer:  # __exit__ of timer will hold thread by time.sleep()
                    with self.__context.gl:
                        self.call_predraw_callback()
                        self.draw()
                        self.call_postdraw_callback()
                        glfw.swap_buffers()
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
        with self.__context.glfw as glfw:
            glfw.hide_window()  # <- glfw window still alive here
            self._render_thread.join()
            self.__context.context_master.remove_window(self)
            glfw.destroy_window()  # <- window destoied here

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
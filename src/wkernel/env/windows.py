import threading
import time

from wkernel.env.windowing.bits import DrawInterface
from .context import ContextManager
from .windowing import *
from ..hooked import *


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
        Windows().init_glfw()
        Windows().reg_window(self)

        self._context_manager = ContextManager()
        if isinstance(shared, Window):
            shared = shared.__glfw_window
        self.__glfw_window = glfw.create_window(width, height, name, monitor, shared)

        # per window init setting
        glfw.make_context_current(self.__glfw_window)
        gl.glEnable(gl.GL_SCISSOR_TEST)
        gl.glEnable(gl.GL_BLEND)
        # self._callback_handler.set_key_callback()
        glfw.make_context_current(None)

        # make view object
        self.__glyph = GlyphNode(0, 0, width, height, None, None, None, None)
        glfw.set_window_close_callback(self.__glfw_window, self.__close_window)

        self._render_thread = threading.Thread(target=self.__run)
        self._pipelines = []

        self.__frame_rate = 30
        self.__timer = Timer(self.__frame_rate)
        self.__num_draw_frame = None
        self.__frame_count = 0

        # managers
        self.__pane_manager = PaneManager(self)
        self.__camera_manager = CameraManager(self)
        self.__device_manager = DeviceManager(self)

        # default camera
        self.__camera_manager[0].body.builder.in3_aspect_ratio = self.__pane_manager[0].glyph.aspect_ratio

    def __enter__(self):
        # syntax for recording basic rendering
        # TODO: make batch rendering. Currently direct drawing
        glfw.make_context_current(self.__glfw_window)  # set context to draw things
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @property
    def glyph(self) -> GlyphNode:
        """
        implementation of abstract method
        :return:
        """
        return self.__glyph

    @property
    def cameras(self) -> CameraManager:
        """
        return CameraManager which handles cameras of this window

        :return:
        """
        return self.__camera_manager

    @property
    def panes(self) -> PaneManager:
        """
        return PaneManager which handles view areas on the window
        :return:
        """

        return self.__pane_manager

    @property
    def devices(self) -> DeviceManager:
        """
        return DeviceManager which handles keyboard and mouse operation

        :return:
        """
        return self.__device_manager

    @property
    def is_current(self):
        return self == Windows().get_current()

    @property
    def current_window(self):
        return Windows().get_current()

    @property
    def framerate(self):
        """
        window render frame rate per sec

        :return:
        """
        return self.__frame_rate

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

    @property
    def glfw_window(self):
        """
        read only glfw window

        :return: glfw window context
        """
        return self.__glfw_window

    def append_pipeline(self, pipeline):
        self._pipelines.append(pipeline)

    def __run(self):
        """
        Rendering thread incuding operations per-frame

        :return:
        """
        # bind and as this is a rendering happends in dedicated thread no need to unbind
        glfw.make_context_current(self.__glfw_window)

        while not glfw.window_should_close(self.__glfw_window):
            if self.__frame_count == self.__num_draw_frame:
                break  # if number of drawn frame is targeted number of frame drawn
            with self.__timer:  # __exit__ of timer will hold thread by time.sleep()
                # gl.glClearColor(1,1,1,1)
                # gl.glClear(gl.GL_COLOR_BUFFER_BIT)
                self.draw()
                glfw.swap_buffers(self.__glfw_window)
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
        glfw.hide_window(self.__glfw_window)  # <- glfw window still alive here
        self._render_thread.join()
        Windows().dereg_window(self)
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

    def run(self, num_draw_frame=None):
        """
        Main function running application

        :param num_draw_frame: int number of frames to draw
        :return:
        """
        Windows().run(num_draw_frame)

    def draw(self):
        """
        glfw, OpenGL placeholder to be overridden by the user

        :return:
        """

    def setup(self):
        pass

    #
    #
    # def key_callback(self, window, key, scancode, action, mods):
    #     print(key, scancode, action, mods)
    #
    # def char_callback(self, window, codepoint):
    #     print('char callback', codepoint)
    #
    # def char_mods_callback(self, window, codepoint, mods):
    #     print('char mods callback', codepoint, mods)


@Singleton
class Windows():
    """
    Class for organizing multiple window insatnces.

    This includes control over main rendering loop
    and some global operation among window instances like creating a new window.
    """
    _windows = []
    _timer = Timer(120)
    _is_glfw_inited = False

    @classmethod
    def init_glfw(cls):
        if not cls._is_glfw_inited:
            glfw.init()
            cls._is_glfw_inited = True

    @classmethod
    def reg_window(cls, window):
        """
        Register window object
        :param window:
        :return:
        """
        if not isinstance(window, Window):
            raise TypeError
        cls._windows.append(window)

    @classmethod
    def dereg_window(cls, window):
        """
        Exclude window object from list

        Make main thread loose track of window object
        :param window:
        :return:
        """
        cls._windows.remove(window)

    @classmethod
    def run(cls, num_draw_frame=None):

        """
        Main loop for operating, drawing a windows
        :return:
        """
        # to insist window drawing only after this function is called
        # thread start is moved from Window().__init__ to here

        for window in cls._windows:
            window.set_num_draw_frame(num_draw_frame)
            window._render_thread.start()
        # main thread. all function calls that has to work in full speed should be here
        while cls._windows:
            with cls._timer:
                glfw.poll_events()
        glfw.terminate() # no window alive means end of opengl functionality

    @classmethod
    def get_current(cls) -> Window:
        # find bound window from window list
        current_context = glfw.get_current_context()
        try:
            current_context.contents
        except:
            # when 'ValueError : NULL pointer access'
            return None
            raise Exception('No context is current')

        # find window
        for window in cls._windows:
            if window.glfw_window.contents.__reduce__() == current_context.contents.__reduce__():
                return window
        raise Exception("Window untrackable")


if __name__ == '__main__':
    window1 = Windows.new_window(400, 400, 'main window')
    window2 = Windows.new_window(500, 500, 'second')
    Windows.run()
    # glfw.create_window(100,100,'1',None,None)/
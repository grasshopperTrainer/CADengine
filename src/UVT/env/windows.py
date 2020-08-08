import threading
import time
from .context import ContextManager
from .windowing import *
from my_patterns import Singleton
from UVT.env.windowing.bits import DrawBit, CallbackMaster

from ..hooked import *


class Timer:
    """
    Time recorder for maintaining given fps
    """
    def __init__(self, target_fps):
        self._marked_time = 0
        self._tfps = target_fps     # target frame per second
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


class Window(CallbackMaster, DrawBit):
    """
    Class for baking exact instance that's on screen

    """
    def __init__(self, width, height, name, monitor=None, shared=None, **kwargs):
        super().__init__()
        Windows().init_glfw()
        Windows().reg_window(self)

        self._context_manager = ContextManager()
        if isinstance(shared, Window):
            shared = shared._glfw_window
        self._glfw_window = glfw.create_window(width, height, name, monitor, shared)

        # per window init setting
        glfw.make_context_current(self._glfw_window)
        gl.glEnable(gl.GL_SCISSOR_TEST)
        self._callback_handler = CallbackManager(self)
        self._callback_handler.set_key_callback()
        glfw.make_context_current(None)

        # make view object
        self._glyph = Glyph(width, height, None, None)

        glfw.set_window_close_callback(self._glfw_window, self._close_window)

        self._render_thread = threading.Thread(target=self._run)
        self._pipelines = []

        self._frame_rate = 30
        self._timer = Timer(self._frame_rate)
        self._frame_to_render = None
        self._frame_count = 0

        self._views = Views(self)
        self._cameras = Cameras(self)

        self._cameras[0].body.builder.in3_ratio = self._views[0].aspect_ratio

    @property
    def cameras(self):
        return self._cameras

    def append_pipeline(self, pipeline):
        self._pipelines.append(pipeline)

    def _run(self):
        """
        Rendering thread incuding operations per-frame
        :return:
        """
        # bind and as this is a rendering happends in dedicated thread no need to unbind
        glfw.make_context_current(self._glfw_window)

        while not glfw.window_should_close(self._glfw_window):
            if self._frame_count == self._frame_to_render:
                break   # if number of drawn frame is targeted number of frame drawn
            with self._timer:   # __exit__ of timer will hold thread by time.sleep()
                gl.glClearColor(1,1,1,1)
                gl.glClear(gl.GL_COLOR_BUFFER_BIT)
                self.draw()
                glfw.swap_buffers(self._glfw_window)
            self._frame_count += 1


    def _close_window(self, window):
        # if not joined, glfw function can be called where there is no glfw context
        # anymore. Downside of joining is that window destruction will only occur
        # when draw waiting is over - meaning destruction only takes place after a frame
        # this can cause 'noticable stall' when fps is very low
        self._render_thread.join()
        Windows().dereg_window(self)
        glfw.destroy_window(window)

    def __enter__(self):
        # syntax for recording basic rendering
        # TODO: make batch rendering. Currently direct drawing
        glfw.make_context_current(self._glfw_window)   # set context to draw things
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # glfw.make_context_current(None)
        # exit rendering recording
        pass

    def set_frame_to_render(self, v):
        self._frame_to_render = v

    @property
    def is_current(self):
        return self == Windows().get_current()

    @property
    def current_window(self):
        return Windows().get_current()


    # @property
    # def render(self):
    #     return self._render_registry._register

    def run(self, frame_count=None):
        Windows().run(frame_count)

    @property
    def framerate(self):
        return self._frame_rate
    @framerate.setter
    def framerate(self, v):
        self._frame_rate = v
        self._timer.tfps = v

    def key_callback(self, window, key, scancode, action, mods):
        print(key, scancode, action, mods)
    def char_callback(self, window, codepoint):
        print('char callback', codepoint)
    def char_mods_callback(self, window, codepoint, mods):
        print('char mods callback', codepoint, mods)


@Singleton
class Windows():
    """
    Class for organizing multiple window insatnces.

    This includes control over main rendering loop
    and some global operation among window instances like creating a new window.
    """
    _windows = []
    _timer = Timer(60)
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
    def run(cls, frame_count=None):

        """
        Main loop for operating, drawing a windows
        :return:
        """
        # to insist window drawing only after this function is called
        # thread start is moved from Window().__init__ to here

        for window in cls._windows:
            window.set_frame_to_render(frame_count)
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
            if window._glfw_window.contents.__reduce__() == current_context.contents.__reduce__():
                return window
        raise Exception("Window untrackable")


if __name__ == '__main__':
    window1 = Windows.new_window(400, 400, 'main window')
    window2 = Windows.new_window(500, 500, 'second')
    Windows.run()
    # glfw.create_window(100,100,'1',None,None)/
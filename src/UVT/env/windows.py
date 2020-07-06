import threading
import time
from .context import GLFW_GL_Context
from .windowing.window_properties import *
from .MVC import View
import glfw


class Windows:
    """
    Class for organizing multiple window insatnces.

    This includes control over main rendering loop
    and some global operation among window instances like creating a new window.
    """
    _windows = []

    @classmethod
    def new_window(cls, width, height, name, monitor=None, shared=None, **kwargs):
        """
        Returns window instance
        :param width:
        :param height:
        :param name:
        :param monitor:
        :param shared:
        :param kwargs:
        :return:
        """
        window = Window(cls, width, height, name, monitor, shared, **kwargs)
        cls._windows.append(window)
        return window

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

            GLFW_GL_Context.glfw.poll_events()

        GLFW_GL_Context.glfw.terminate() # no window alive means end of opengl functionality

    @classmethod
    def get_current(cls):
        # find bound window from window list
        current_context = glfw.get_current_context()
        try:
            current_context.contents
        except:
            # when 'ValueError : NULL pointer access'
            raise Exception('No context is current')

        # find window
        for window in cls._windows:
            if window._glfw_window.contents.__reduce__() == current_context.contents.__reduce__():
                return window
        raise Exception("Window untrackable")


class Window(View):
    """
    Class for baking exact instance that's on screen

    """
    def __init__(self, windows, width, height, name, monitor=None, shared=None, **kwargs):
        self._windows = windows
        self._context = GLFW_GL_Context(**kwargs)
        if isinstance(shared, Window):
            shared = shared._glfw_window
        self._glfw_window = self._context.glfw.create_window(width, height, name, monitor, shared)
        self._per_window_init_setting()


        # make view object
        super().__init__(0, 0, w=width, h=height, mother=None)

        self._context.glfw.set_window_close_callback(self._glfw_window, self._close_window)

        self._timer = Timer(30)
        self._render_thread = threading.Thread(target=self._run)
        self._pipelines = []

        self._frame_to_render = None
        self._frame_count = 0

        self._render_registry = RenderRegistry(self)

    def _per_window_init_setting(self):
        """
        Initial settings per window(context)
        :return:
        """
        self.glfw.make_context_current(self._glfw_window)

        self.gl.glEnable(self.gl.GL_SCISSOR_TEST)

        self.glfw.make_context_current(None)

    @property
    def lyrs(self):
        return self._render_registry._layers
    @property
    def viws(self):
        return self._render_registry._views
    @property
    def cams(self):
        return self._render_registry._cameras

    def append_pipeline(self, pipeline):
        self._pipelines.append(pipeline)

    def _run(self):
        """
        Rendering thread incuding operations per-frame
        :return:
        """
        while not self._context.glfw.window_should_close(self._glfw_window):
            if self._frame_count == self._frame_to_render:
                break   # if number of drawn frame is targeted number of frame drawn

            with self._timer:   # __exit__ of timer will hold thread by time.sleep()
                with self:
                    self.gl.glClearColor(0.3, 1, 0.3, 1.0)
                    self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT)
                    self._render_registry._render()
                    self._context.glfw.swap_buffers(self._glfw_window)

            self._frame_count += 1


    def _close_window(self, window):
        # if not joined, glfw function can be called where there is no glfw context
        # anymore. Downside of joining is that window destruction will only occur
        # when draw waiting is over - meaning destruction only takes place after a frame
        # this can cause 'noticable stall' when fps is very low
        self._render_thread.join()
        self._windows._windows.remove(self)
        self._context.glfw.destroy_window(window)

    def __enter__(self):
        # syntax for recording basic rendering
        # TODO: make batch rendering. Currently direct drawing
        self._context.glfw.make_context_current(self._glfw_window)   # set context to draw things
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._context.glfw.make_context_current(None)
        # exit rendering recording
        pass

    def set_frame_to_render(self, v):
        self._frame_to_render = v

    @property
    def is_current(self):
        return self == self._windows.get_current()

    @property
    def gl(self):
        """
        Purly part of UI.
        :return:
        """
        return self._context.gl

    @property
    def glfw(self):
        """
        Purly part of UI.
        :return:
        """
        return self._context.glfw

    @property
    def render(self):
        return self._render_registry._register


class Timer:
    """
    Time recorder for maintaining given fps
    """
    def __init__(self, target_fps):
        self._marked_time = 0
        self._target_fps = target_fps
        self._tpf = 1/target_fps    # time per frame

    def __enter__(self):
        self._marked_time = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        loop_duration = time.time() - self._marked_time
        wait = self._tpf - loop_duration
        if wait >= 0:
            time.sleep(wait)


if __name__ == '__main__':
    window1 = Windows.new_window(400, 400, 'main window')
    window2 = Windows.new_window(500, 500, 'second')
    Windows.run()
    # glfw.create_window(100,100,'1',None,None)/
import threading
import time
from env.context import My_glfw


class Windows:
    """
    Class for organizing window insatnces.

    This includes control over main rendering loop
    and some global operation among window instances like creating a new one.
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
    def run(cls):
        """
        Main loop for operating, drawing a windows
        :return:
        """
        # to insist window drawing only after this function is called
        # thread start is moved from WIndow().__init__ to here
        for window in cls._windows:
            window._render_thread.start()
        # main thread. all function calls that has to work in full speed should be here
        while cls._windows:
            My_glfw.poll_events()

        My_glfw.terminate() # no window alive means end of opengl functionality


class Window:
    """
    Class for baking exact instance that's on screen

    """
    def __init__(self, windows, width, height, name, monitor=None, shared=None, **kwargs):
        self._windows = windows
        self._context = My_glfw(**kwargs)
        self._glfw_window = self._context.create_window(width, height, name, monitor, shared)

        self._context.set_window_close_callback(self._glfw_window, self._close_window)

        self._timer = Timer(30)
        self._render_thread = threading.Thread(target=self._run)

    def _run(self):
        """
        Rendering thread incuding operations per-frame
        :return:
        """
        while not self._context.window_should_close(self._glfw_window):
            with self._timer:   # __exit__ of timer will hold thread by time.sleep()
                self._context.swap_buffers(self._glfw_window)


    def _close_window(self, window):
        # if not joined, glfw function can be called where there is no glfw context
        # anymore. Downside of joining is that window destruction will only occur
        # when draw waiting is over - meaning destruction only takes place after a frame
        # this can cause 'noticable stall' when fps is very low
        self._render_thread.join()
        self._windows._windows.remove(self)
        self._context.destroy_window(window)


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
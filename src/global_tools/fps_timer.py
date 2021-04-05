import time


class FPSTimer:
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

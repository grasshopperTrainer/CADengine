from wkernel.devices.render.panes import PaneManager
from wkernel.devices.render.cameras import CameraManager
from wkernel.devices.input.base import Mouse, Keyboard
from global_tools.trackers import TypewiseTracker


class DeviceMaster:
    """
    Control group of devices
    """

    def __init__(self, window):
        self.__window = window
        # database
        self._tracker = TypewiseTracker()

        # of input
        self.__mouse = Mouse(window)
        self.__keyboard = Keyboard(window)
        # of render
        self.__panes = PaneManager(self)
        self.__cameras = CameraManager(self)

    @property
    def window(self):
        return self.__window

    @property
    def mouse(self) -> Mouse:
        return self.__mouse

    @property
    def keyboard(self) -> Keyboard:
        return self.__keyboard

    @property
    def cameras(self) -> CameraManager:
        return self.__cameras

    @property
    def panes(self) -> PaneManager:
        return self.__panes

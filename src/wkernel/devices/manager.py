from wkernel.devices.render.panes import PaneManager
from wkernel.devices.render.cameras import CameraManager
from wkernel.devices.input.base import Mouse, Keyboard


class DeviceManager:
    """
    Control group of devices
    """

    def __init__(self, window):
        self._window = window

        self.__mouse = Mouse(window, self)
        self.__keyboard = Keyboard(window, self)

        # managers
        self.__panes = PaneManager(window)
        self.__cameras = CameraManager(window)

    @property
    def mouse(self):
        return self.__mouse

    @property
    def keyboard(self):
        return self.__keyboard

    @property
    def cameras(self):
        return self.__cameras

    @property
    def panes(self):
        return self.__panes

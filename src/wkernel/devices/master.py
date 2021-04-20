from wkernel.devices.render.pane.base import PaneManager
from wkernel.devices.render.cameras import CameraManager
from wkernel.devices.render.frame import FrameManager
from wkernel.devices.render.cursor import CursorManager

from wkernel.devices.input.base import Mouse, Keyboard
from ckernel.tools.stacker import TypewiseStacker


class DeviceMaster:
    """
    Control group of devices
    """

    def __init__(self, window):
        self.__window = window
        # database
        self.__stacker = TypewiseStacker()

        # of input
        self.__mouse = Mouse(window)
        self.__keyboard = Keyboard(window)
        # of render
        self.__panes = PaneManager(self)
        self.__cameras = CameraManager(self)
        self.__frames = FrameManager(self)
        self.__cursors = CursorManager(self)

    @property
    def stacker(self) -> TypewiseStacker:
        return self.__stacker

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

    @property
    def frames(self) -> FrameManager:
        return self.__frames

    @property
    def cursors(self) -> CursorManager:
        return self.__cursors

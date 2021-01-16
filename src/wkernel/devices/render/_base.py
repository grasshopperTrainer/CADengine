import abc


class RenderDevice(metaclass=abc.ABCMeta):
    """
    Instance of render target types
    """
    def __init__(self, manager):
        self.__manager = manager

    @property
    def manager(self):
        """
        Render target pool is seen as a 'manager' from its target
        :return:
        """
        return self.__manager


class RenderDeviceManager:
    """
    Collector of render devices.
    """
    def __init__(self, window):
        self.__window = window
        self._devices = []
        self._current_target_stack = []

    def __getitem__(self, item) -> RenderDevice:
        raise NotImplementedError

    def _appendnew_device(self, target):
        self._devices.append(target)

    def current_target(self):
        if self._current_target_stack:
            return self._current_target_stack[-1]
        return None

    @property
    def window(self):
        return self.__window

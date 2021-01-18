import abc
from global_tools.trackers import *


class RenderDevice(metaclass=abc.ABCMeta):
    """
    Instance of render target types
    """
    def __init__(self, manager):
        """
        :param manager:
        """
        # giving registration responsibility to the terminal deivce
        self.__manager = manager

    # should provide context manager
    def __enter__(self):
        self.__manager.master._tracker.stack.push(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__manager.master._tracker.stack.pop(self.__class__)

    @property
    def manager(self):
        """
        Render target pool is seen as a 'manager' from its target
        :return:
        """
        return self.__manager

    def get_current(self):
        """
        get current from tracker
        :return:
        """
        return self.__manager.master._tracker.stack.get_current(self.__class__)


class RenderDeviceManager(metaclass=abc.ABCMeta):
    """
    ! inherit must

    Collector of render devices.
    Expand through inheritance. Add device managing methods.
    """

    def __init__(self, master):
        self.__master = master

    def __getitem__(self, item) -> RenderDevice:
        return self.__master._tracker.registry[self.device_type][item]

    def appendnew_device(self, device):
        """
        register device and return new device

        :return:
        """
        self.__master._tracker.registry.register(device)

    @property
    @abc.abstractmethod
    def device_type(self):
        return self.__device_type

    @property
    def current(self):
        return self.__master._tracker.stack.get_current(self.device_type)

    @property
    def master(self):
        """
        master passer
        :return:
        """
        return self.__master

    @property
    def window(self):
        """
        window passer

        :return:
        """
        return self.__master.window

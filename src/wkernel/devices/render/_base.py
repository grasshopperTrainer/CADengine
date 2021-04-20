import abc


class RenderDeviceManager(metaclass=abc.ABCMeta):
    """
    ! inherit must

    Collector of render devices.
    Expand through inheritance. Add device managing methods.
    """

    def __init__(self, master):
        self.__master = master
        self.__device_idx = 0
        self.__devices = {}

    def __getitem__(self, item):
        return self.__devices[item]
        # return self.__master.tracker.registry[self.device_type][item]

    def __len__(self):
        return len(self.__master.stacker.registry[self.device_type])

    def _appendnew_device(self, device):
        """
        register new device

        :return:
        """
        self.__devices[self.__device_idx] = device
        self.__device_idx += 1

        # self.__master.tracker.registry.register(device)

    @property
    @abc.abstractmethod
    def device_type(self):
        return self.__device_type

    @property
    def current(self):
        return self.__master.stacker[self.device_type].peek()

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

    def enter(self):
        self.__manager.master.stacker.push(self)
        return self

    def exit(self):
        self.__manager.master.stacker[self.__class__].pop()

    # inheritor should provide context manager
    # but not through super just to notify IDE about the return type
    def __enter__(self):
        return self.enter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.exit()

    @property
    def manager(self) -> RenderDeviceManager:
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
        return self.__manager.master.stacker[self.__class__].peek()


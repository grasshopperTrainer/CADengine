class enum:
    def __init__(self, cls):
        self.__val_set = set()
        self.__arg_list = []

        d = {}
        for k, v in cls.__dict__.items():
            if not (k.startswith('__') and k.endswith('__')):
                if not isinstance(v, enum):  # avoid sub enum
                    v = EnumVal(v)
                self.__arg_list.append((k, v))
                self.__val_set.add(v)
                d[k] = v

        self.__ins = type(cls.__name__, (cls,), d)()

    def __getattr__(self, item):
        return self.__ins.__getattribute__(item)

    def __getitem__(self, item):
        return self.__arg_list[item][1]

    def __contains__(self, item):
        return item in self.__val_set

    def __iter__(self):
        return iter(self.__arg_list)

    def __str__(self):
        return f"<Enumerated: {self.__ins.__class__.__name__}>"

    def has_member(self, ev):
        """
        checks if given enum value is a member

        ! this method tests if value is subordinate
        which makes this distinguishable from __contains__
        :param ev: enum value
        :return:
        """
        if not isinstance(ev, EnumVal):
            raise TypeError
        if ev in self:
            return True
        else:
            for k, v in self.__arg_list:
                if isinstance(v, enum):
                    if v.has_member(ev):
                        return True
        return False


class EnumVal:
    def __init__(self, v):
        self.__v = v

    def __str__(self):
        return self.__v.__str__()

    def __repr__(self):
        return f"<enum: {self.__v.__str__()}>"

    @property
    def v(self):
        return self.__v

class enum:
    def __init__(self, cls):
        self.__val_set = set()
        self.__arg_list = []

        # auto wrap attributes
        d = {}
        for k, v in cls.__dict__.items():
            if not (k.startswith('__') and k.endswith('__')):
                if not isinstance(v, (enum, EnumAttr)):  # avoid sub enum
                    v = EnumAttr(v)
                self.__arg_list.append((k, v))
                self.__val_set.add(v)
                d[k] = v

        # force singleton
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
        if not isinstance(ev, EnumAttr):
            raise TypeError
        if ev in self:
            return True
        else:
            for k, v in self.__arg_list:
                if isinstance(v, enum):
                    if v.has_member(ev):
                        return True
        return False


class EnumAttr:
    def __init__(self, rep_val, **kwargs):
        """
        Simple Enum object -> Enum that doesn't have methods.

        :param rep_val: representative value, or None, its always retrived by `val`
        :param kwargs: optional attributes
        """
        # to go around self.__setattr__
        self.__dict__['rep_val'] = rep_val
        for k, val in kwargs.items():
            if k in self.__dict__:
                raise AttributeError
            self.__dict__[k] = val

    def __setattr__(self, key, value):
        # denied
        raise

    def __str__(self):
        return f"<enum: {self.rep_val.__str__()}>"

    @property
    def val(self):
        """
        return representative value of this enum
        :return:
        """
        return self.rep_val


if __name__ == '__main__':
    @enum
    class Fruit:
        apple = None

    @enum
    class Company:
        apple = None

    print(Fruit.apple, Company.apple)
    # print(Fruit.apple.n, Company.apple.n)

    print(Fruit.apple == Company.apple)
import weakref


class _enumProp:
    def __init__(self, val):
        self._val = val

    def __get__(self, instance, owner):
        return self._val

    def __set__(self, instance, value):
        raise Exception('enum property immutable')


class enum:
    def __init__(self, cls):
        self.__ins = cls()
        cls.__contains__ = self.__contains

    def __get__(self, instance, owner):
        return self.__ins

    @staticmethod
    def __contains(self, item):
        for k, v in self.__class__.__dict__.items():
            if isinstance(v, _enumProp):
                if v._val == item:
                    return True
        return False

    @staticmethod
    def prop(val):
        return _enumProp(val)

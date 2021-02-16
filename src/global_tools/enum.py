import weakref

class _enumProp:
    def __init__(self, val):
        self.__val = val

    def __get__(self, instance, owner):
        return self.__val

    def __set__(self, instance, value):
        raise Exception('enum property immutable')


class enum:

    def __init__(self, cls):
        self.__ins = cls()

    def __get__(self, instance, owner):
        return self.__ins

    @staticmethod
    def prop(val):
        return _enumProp(val)
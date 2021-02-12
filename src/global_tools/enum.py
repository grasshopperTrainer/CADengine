import weakref

class _enumProp:
    def __init__(self, val):
        self.__val = val

    def __get__(self, instance, owner):
        return self.__val


class enum:
    def __new__(cls):
        return cls

    @staticmethod
    def prop(val):
        return _enumProp(val)
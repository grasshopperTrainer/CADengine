"""
Singleton class example
"""

class SingletonClass:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            ins = super().__new__(cls)
            cls._instance = ins
            return ins

        if '__init__' in cls._instance.__class__.__dict__:
            delattr(cls._instance.__class__, '__init__')
        return cls._instance


class A(SingletonClass):

    def __init__(self):
        print('initiation A')
    pass

a = A()
b = A()
c = A()
print(a, b, c)
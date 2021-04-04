class M(type):
    def __new__(cls, clsname, bases, dct):
        typ = super().__new__(cls, clsname, bases, dct)
        print(typ)
        return typ(10, 20)

class A(metaclass=M):


    def __init__(self, a, b):

        print('initing')
        self.a = a
        self.b = b
a = A()
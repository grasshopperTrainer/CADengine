class A:
    pass

a = A()

class B(a):
    def __new__(cls, *args, **kwargs):
        print(args, kwargs)
    pass
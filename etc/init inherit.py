class K:
    def __init__(self,a,b):
        print('init K')
        self.a = a

class A:
    def __init__(self, a, b):
        print('init A')

class B:
    def __new__(cls, *args, **kwargs):
        print('new of B', cls, args, kwargs)
        return super().__new__(cls)

    def __init__(self, a, b):
        print('init B')

class C(type):
    def __new__(cls, name, bases, dct):
        bases = (B, *bases)
        return super().__new__(cls, name, bases, dct)
    # def __init__(self):
    #     print('init C')
    pass

class D(K, dict):
    pass
    # def __init__(self, a, b):
    #     pass

k = C('k', (str,), {})(10, 20)

b = type('b', (A, str), {})
print(b.__new__(b))
d = D(10, 20)
print(type(d), isinstance(d, K), isinstance(d, dict))
print(d)
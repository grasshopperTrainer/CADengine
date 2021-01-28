class Meta(type):
    def __new__(cls, clsname, bases, dct):
        print('calling meta new')
        return super().__new__(cls, clsname, bases, dct)

    def __init__(self, *args, **kwargs):
        print(self, *args, **kwargs)
        # self.value = value

    def __instancecheck__(self, instance):
        print(instance)

class A(metaclass=Meta):
    def __init__(self, v):
        self.value = v

a = A(10)
print(a.value)
print(isinstance(A, int))
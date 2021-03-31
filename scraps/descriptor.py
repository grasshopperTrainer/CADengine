

class D:
    def __init__(self, name):
        self._name = '_'+name

    def __set__(self, instance, value):
        print('setting')
        setattr(instance, self._name, value)

    def __get__(self, instance, owner):
        print('getting')
        return getattr(instance, self._name)

class C:
    a = D('a')
    def __init__(self):
        self.a = 10

c = C()
print(c.a)
print(c._a)
c._a = 20
print(c.a, c._a)
c.a = 30

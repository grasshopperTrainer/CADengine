import weakref as wr

class A:
    def __init__(self):
        self.v = 10
a = A()

b = wr.ref(a)
c = wr.proxy(a)
# print(a, a.v)
# print(b, b().v)
# print(c, c.v)
del a
print(b)
print(c())
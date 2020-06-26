class K:
    def __init__(self, a, b):
        self.a = a
        self.b = b
# class M(type):
#     def __instancecheck__(self, instance):
#         print(instance, 'ddd')

def __instancecheck__(self, instance):
    print('instancecheck')

class C:
    def __init__(self, obj):
        self.obj = obj
        # self.__class__ = type(self.obj)

    def foo(self):
        print('foo of C')


l = K(10, 'ten')
c = C(l)
for k, v in l.__dict__.items():
    setattr(c, k, v)

print(c.a, c.b, c.obj)
print(isinstance(c, type))

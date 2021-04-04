class M:
    _wrapper_classes= {}
    def __new__(cls, a,b,c,d):
        typ = type('A', (A, type(d)), {})
        print('ddd')
        inst = typ(a,b,c,d)
        print('kkk')
        return inst

class A:
    def __init__(self, *args, **kwargs):
        instance, name, sign, value = args
        super.__init__(self, value)
        self._intf_holder = instance
        self._intf_is_deleted = False
        self._intf_name = name
        self._intf_sign = sign
        self._intf_obj = value  # real value wrapped

    def __str__(self):
        return 'ddd'


a = M(10,20,30,40)
b = M('s')
print(a)
print(id(type(a)), id(type(b)))
print(isinstance(a, int))
print(isinstance(a, A))
print(isinstance(a, type(20)))
import weakref as wr


class IntfObj:
    """
    Wrapper storing additional properties to wrapped type
    """

    def __init__(self, instance, name, kind, value):
        """
        Store interface properties
        :param instance:
        :param name:
        :param kind:
        :param value:
        :return:
        """
        self._intf_instance = wr.ref(instance)
        self._intf_is_updated = True
        self._intf_is_deleted = False
        self._intf_name = name
        self._intf_kind = kind
        self._intf_obj = value  # real value wrapped

    def __str__(self):
        return f"< {self._intf_kind} : {self._intf_obj} >"

    @property
    def intf_name(self):
        return self._intf_name

    @property
    def intf_holder(self):
        ins = self._intf_is_updated()
        if ins is None:
            raise NotImplementedError
        return ins

    @property
    def intf_is_updated(self):
        return self._intf_is_updated

    @property
    def intf_kind(self):
        return self._intf_kind

    @property
    def intf_is_deleted(self):
        return self._intf_is_deleted

    @property
    def real_value(self):
        return self._intf_obj

    def __add__(self, other):
        return self.real_value.__add__(other)

    def __sub__(self, other):
        return self.real_value.__sub__(other)

    def __truediv__(self, other):
        return self.real_value.__truediv__(other)

    def __floordiv__(self, other):
        return self.real_value.__floordiv__(other)

    def __mul__(self, other):
        return self.real_value.__mul__(other)


# class IntfObjType(type):
#     """
#     Interface wrapped type builder
#
#     Builds new type inheriting type of wrapped value.
#     By doing this the wrapped object can fully respond like the original object.
#     It can evan pass (def) isinstance query.
#     """
#     _type_class = {}
#
#     def __new__(cls, ori_obj):
#         if ori_obj is None:
#             return None
#         ori_typ = type(ori_obj)
#         # to have single class wrapping a type
#         if ori_typ in cls._type_class:
#             return cls._type_class[ori_typ]
#
#         # else build new and force inherit (class) IntfObj that holds additional prop as interface
#         clsname = f"Intf_{ori_typ.__name__.capitalize()}"
#         bases = (ori_typ, IntfObj)
#
#         clss = super().__new__(cls, clsname, bases, {})
#         if issubclass(clss, (int, float, list, tuple, set, dict)):
#             clss.__init__ = ori_typ.__init__
#         else:
#             clss.__init__ = IntfObj.__init__
#
#         # register
#         cls._type_class[ori_typ] = clss
#         return clss
#
#     # def __init__(self, *args, **kwargs):
#     #     self._wrapper_instance = None
#     #     self._wrapper_name = None
#     #     self._wrapper_kind = None
#     #     self._wrapper_value = None


class Interface:
    """
    Interface node for input and output

    To control setting value
    """

    def __init__(self, name, def_val):
        self._name = name
        self._record_name = f'_{self._kind}_{name}'
        self._def_val = def_val

    def _init_interface(self, instance):
        """
        Guarantee there is the attribute and record of attributes
        :param instance:
        :return:
        """
        if not hasattr(instance, self._record_name):
            if self._def_val is None:
                intf_obj = None

            if self._def_val is not None:
                # build Interface Object type and object
                intf_obj = self._build_intf_obj(instance, self._def_val)
            instance.__dict__.setdefault('_' + self._kind + 's', set()).add(self._record_name)
            setattr(instance, self._record_name, intf_obj)

    def _build_intf_obj(self, instance, val):
        return IntfObj(instance, self._name, self._kind, val)

    def _set_output_need_update(self, instance):
        """
        Set all outputs updated
        :param instance:
        :return:
        """
        if hasattr(instance, '_outputs'):
            for att_name in instance._outputs:
                instance.__dict__[att_name]._intf_is_updated = True
                # getattr(instance, att_name)._intf_need_update = True

    def _update_upstream(self, instance):
        """
        Follows chain of interface backward and update values
        :param instance:
        :return:
        """
        need_calc = False
        # look through all inputs and check if any update has been made
        for attr_name in instance.__dict__.get('_inputs', []):
            intf_obj = getattr(instance, attr_name)
            if intf_obj.intf_is_updated:
                getattr(intf_obj.intf_holder, intf_obj.intf_name)  # recursion
                intf_obj._intf_is_updated = False
                need_calc = True

        for attr_name in instance.__dict__.get('_outputs', []):
            intf_obj = getattr(instance, attr_name)
            if intf_obj.intf_is_updated:
                need_calc = True

        if need_calc:
            instance.operate()  # operate is an assigned name
            # set all outputs updated
            self._set_output_need_update(instance)


class Input(Interface):
    """
    Designate input value
    """
    _kind = 'input'

    def __set__(self, instance, value):
        """
        Handles assigning python primitive to InterfaceValueContainer
        :param instance:
        :param value:
        :return:
        """
        self._init_interface(instance)

        if isinstance(value, IntfObj):  # if connecting output input interfaces
            if value.intf_kind == 'input':
                raise AttributeError("direction should be (output) -> (input)")
            instance.__dict__[self._record_name] = value
            value._intf_is_updated = True
        else:  # if putting raw value
            setattr(instance, self._record_name, self._build_intf_obj(instance, value))

        # mark outputs updated so inputs referensing it can triger (def) operate
        self._set_output_need_update(instance)

    def __get__(self, instance, owner) -> IntfObj:
        self._init_interface(instance)
        # if interface is deleted replace it with default value
        intf_obj = getattr(instance, self._record_name)
        if intf_obj.intf_is_deleted:
            setattr(instance, self._record_name, self._build_intf_obj(instance, self._def_val))
            return getattr(instance, self._record_name)
        # input could have been set to update by its holder
        if intf_obj.intf_holder != instance and intf_obj.intf_is_updated:
            self._update_upstream(intf_obj.intf_holder)

        return intf_obj

    def __delete__(self, instance):
        """
        Disconnection from input

        Returns attribute value to assigned default value
        :param instance:
        :return:
        """
        intf_obj = IntfObj(instance, self._name, self._kind, self._def_val)
        instance.__dict__.setdefault('_' + self._kind + 's', set()).add(self._name)
        setattr(instance, self._record_name, intf_obj)

        # make all outputs updated so it calculates when called
        self._set_output_need_update(instance)


class Output(Interface):
    """
    Designate output value
    """
    _kind = 'output'

    def __set__(self, instance, value):
        self._init_interface(instance)
        # calling within component to set the result of operation
        if instance == getattr(instance, self._record_name).intf_holder:
            value = value.real_value if isinstance(value, IntfObj) else value
            getattr(instance, self._record_name)._intf_obj = value
        else:
            raise AttributeError("Output can't be set explicitly")

    def __get__(self, instance, owner):
        """
        Update output value by recursively looking all Input values
        :param instance:
        :param owner:
        :return:
        """
        self._init_interface(instance)
        self._update_upstream(instance)
        intf_obj = getattr(instance, self._record_name)
        intf_obj._intf_is_updated = False
        return intf_obj

    def __delete__(self, instance):
        """
        Disconnection from output

        1. raise removed flag of intf object so when it's called by another holder,
        it would remove old one and reset with its default value
        2. return output value to pre defined default value

        :param instance:
        :return:
        """

        intf_to_remove = getattr(instance, self._record_name)
        intf_to_remove._intf_is_deleted = True
        setattr(instance, self._record_name, self._build_intf_obj(instance, self._def_val))


class K:
    def __init__(self, a, b):
        self.a = a
        self.b = b


class A:
    a = Input('a', 0)
    a_out = Output('a_out', 0)

    def operate(self):
        self.a_out = self.a
        print('operation A')


class B:
    b = Input('b', 0)
    c = Output('c', 0)

    def operate(self):
        self.c = self.b * 2
        print('operation B')


a = A()
b = B()
print('setting value explicitly')
a.a = 10
print(a.a)
print(a.a_out)
print(a.a_out)
# setting reverse
# a.a_out = b.b

print('simple connection')
b.b = a.a_out
print(b.b)
print('check operation')
print(b.c)
print('check if operation is not called when no change made')
print(b.c)
print(b.b)
print('check update chained')
a.a = 15
print(b.b)
print(b.c)
print('check disconnection from input')
del b.b
print(a.a)
print(a.a_out)
print(b.c)
print('check disconnection from output')
a.a = 100
b.b = a.a_out
print(b.c)
del a.a_out
print()
print(a.a_out)
print(b.c)
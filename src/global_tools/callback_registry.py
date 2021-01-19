import weakref

"""
perpose of these descriptors are to get information of instance calling it.
So it does nothing but return wrapped execution method with instance input.
"""


class _Appender:
    def __get__(self, instance, owner):
        def __wrapper(self, method, *args, **kwargs):
            return instance.append(self, method, *args, **kwargs)

        return __wrapper


class _Enabler:
    def __get__(self, instance, owner):
        def __wrapper(self, v):
            return instance.enable(self, v)

        return __wrapper


class _Remover:
    def __get__(self, instance, owner):
        def __wrapper(self, method):
            return instance.deregister(self, method)

        return __wrapper


class callbackRegistry:
    """
    decorator: register multiple callbacked functions and call them when needed

    # use of decorators
    Like using @property use this class as decorator with callback caller function(A),
    then use method 'appender' of A's returned to decorated appender function.
    Additionally, `enabler` and `remover` decorator is provided to extend functionality.

    # order insensitive execution
    callbacked are not guarantied to be executed in order.
    For order sensitive set of callbacked, simply provide master callbacked
    and call other functions inside that master callback in desired order.

    ! not implemented
    # use of direct methods; append, remove, enable, disable
    For cases where use of the registry is not exposed but only used inside the class,
    all decorations can be omitted. Then one can use direct methods provided.
    !

    # example of simple, full functional implementation:
        class Foo:
            def __init__(self):
                pass

            @callbackRegistry
            def call_a_callback(self, **on_call_kwargs):
                pass

            @call_a_callback.appender
            def append_a_callback(self, func, *args, **kwargs):
                pass

            @call_a_callback.enabler
            def enable_a_callback(self, do_enable):
                pass

            @call_a_callback.remover
            def remove_a_callback(self, method):
                pass

    # dict for in-module doc strings
    caller - function calling all callbacked functions
    calling - operation where caller is called
    callbacked - functions called when caller calls
    """

    __appender = _Appender()
    __enabler = _Enabler()
    __remover = _Remover()

    def __init__(self, _caller):
        """
        decorator wrapping caller method
        wrapped caller may accept kwargs, those put in all callbacked additionally while calling
        besides attributes registered at the moment it was appended with appender

        wrapped caller method is executed at the place where all callbacked has to be called
        :param _caller:
        :return:
        """
        self.__callbacked_record = weakref.WeakKeyDictionary()
        self.__callbacked_record_prop = weakref.WeakKeyDictionary()

    def __get__(self, instance, owner):
        """
        self class is at the same time 'Caller' descriptor

        :param instance:
        :param owner:
        :return:
        """

        def wrapper(**on_call_kwargs):
            return self.call(instance, **on_call_kwargs)

        return wrapper

    def __init_record_needed(self, instance):
        """
        initiate record if its not there

        :param instance:
        :return:
        """
        # initiated if instance not registered
        if instance not in self.__callbacked_record:
            self.__callbacked_record.setdefault(instance, {})
            self.__callbacked_record_prop.setdefault(instance, {'active': True})

    """
    decorator interface
    """

    def appender(self, _):
        """
        this is a decorator for callbacked append function

        decorate functions that append callbacked functions and
        kwargs to be put when calling callbacked afterward

        :return:
        """
        return self.__appender

    def enabler(self, _):
        """
        decorator to decorate enabler function

        :return:
        """
        return self.__enabler

    def remover(self, _):
        """
        decorator to decorate remover function

        :return:
        """
        return self.__remover

    """
    real executors
    """

    def call(self, instance, **on_call_kwarg):
        """
        provided for strudctural consistency, refer to __call__ for real decorator in action

        :param on_call_kwarg:
        :return:
        """
        self.__init_record_needed(instance)
        if not self.__callbacked_record_prop[instance]['active']:
            return
        # calling actual callbacked functions
        for k, (args, wkwargs, skwargs) in self.__callbacked_record.get(instance, {}).items():
            args = (arg() if isinstance(arg, weakref.ref) else arg for arg in args)
            k(*args, **skwargs, **wkwargs, **on_call_kwarg)

    def append(self, instance, callbacked, *args, **kwargs):
        """
        real method executed when appender decorated with __init__ is called

        registry stores a set of values that is needed calling callbacked:
        callbacked - input strong - input weak - input on_call

        making weakref for all to prevent memory leak
        do not strongly store any objects that is not needed calling callbacked

        FIXME: ! memory leak warning for storing callbacked as a key, yet by weak referencing it, method is lost
                 in common situation where callbacked is dedicated function and not used elsewhere.

        :param callbacked: to be called when calling is triggered
        :param kwargs: to be put input callbacked while calling
        :return:
        """
        self.__init_record_needed(instance)

        # store args
        arr = ([], weakref.WeakValueDictionary(), {})
        self.__callbacked_record[instance][callbacked] = arr
        for v in args:
            try:
                arg = weakref.ref(v)
            except TypeError:
                arg = v
            except:
                raise Exception("unknown error while storing input attributes")
            arr[0].append(arg)

        # store kwarg
        # build argument dict but two as builtin such as int cant be weakrefed
        for k, v in kwargs.items():
            try:
                arr[1][k] = v
            except TypeError:
                arr[2][k] = v
            except:
                raise Exception("unknown error while storing input attributes")

    def remove(self, instance, method):
        """
        remove callbacked method

        :param method: method registered as a callbacked
        :return:
        """
        self.__init_record_needed(instance)

        if method not in self.__callbacked_record[instance]:
            raise ValueError("given method doesnt exist in the register")
        self.__callbacked_record[instance].pop(method)

    def enable(self, instance, v):
        """
        enable callback
        :return:
        """
        try:
            v = bool(v)
        except TypeError as e:
            raise e
        self.__init_record_needed(instance)
        self.__callbacked_record_prop[instance]['active'] = v

# if __name__ == '__main__':
#     # example
#
#     class Foo:
#         def __init__(self):
#             pass
#
#         @callbackRegistry
#         def call_a_callback(self, **on_call_kwargs):
#             print('caller')
#
#         @call_a_callback.appender
#         def append_a_callback(self, func, *args, **kwargs):
#             print('appender')
#
#         @call_a_callback.enabler
#         def enable_a_callback(self, do_enable):
#             print('enabler')
#
#         @call_a_callback.remover
#         def remove_a_callback(self, method):
#             print('remover')
#
#
#     f = Foo()
#     ff = Foo()
#
#     class Weakrefable:
#         pass
#
#
#     def a_callback(arg0, arg1, arg2, *args, **kwargs):
#         print('CALLBACKED CALLING')
#         pass
#
#     a = Weakrefable()
#     b = Weakrefable()
#
#     f.append_a_callback(a_callback, 10, a, arg2=10, unknown_arg=b)
#     f.call_a_callback()
#     # print(f.call_a_callback)
#     # print('another instance')
#     # ff.call_a_callback()
#     ff.call_a_callback()
#     ff.enable_a_callback(False)
#     # f.enable_a_callback(False)
#     f.call_a_callback()

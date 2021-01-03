import weakref


class callbackRegistry:
    """
    decorator: register multiple callbacked functions and call them when needed

    # use of decorators
    Like using @property use this class as decorator with callback caller function(A),
    then use method 'appender' of A's returned to decorated appender function.
    Additionally, `enabler` and `remover` decorator is provided to extend functionality.

    # use of direct methods; append, remove, enable, disable
    For cases where use of the registry is not exposed but only used inside the class,
    all decorations can be omitted. Then one can use direct methods provided.

    # order insensitive execution
    callbacked are not guarantied to be executed in order.
    For order sensitive set of callbacked, simply provide master callbacked
    and call other functions inside that master callback in desired order.

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

    def __init__(self, _caller):
        """
        decorator wrapping caller method
        wrapped caller may accept kwargs, those put in all callbacked additionally while calling
        besides attributes registered at the moment it was appended with appender

        wrapped caller method is executed at the place where all callbacked has to be called
        :param _caller:
        :return:
        """
        self.__callback_funcs = weakref.WeakKeyDictionary()
        self.__flag_enable = True

        self.caller(_caller)

    def __call__(self, **on_call_kwarg):
        """
        real method executed when wrapped caller(decorated by self.caller) is executed

        :param on_call_kwarg: arguments to be put when
        :return:
        """
        self.call(on_call_kwarg)

    def call(self, on_call_kwarg):
        """
        provided for strudctural consistency, refer to __call__ for real decorator in action

        :param on_call_kwarg:
        :return:
        """
        if not self.__flag_enable:
            return
        # calling actual callbacked functions
        for k, (args, wkwargs, skwargs) in self.__callback_funcs.items():
            args = (arg() if isinstance(arg, weakref.ref) else arg for arg in args)
            k(*args, **skwargs, **wkwargs, **on_call_kwarg)

    def caller(self, _caller):
        """
        provided for structural consistency, refer to __init__ for real decorator in action

        :param _caller:
        :return:
        """
        pass

    def append(self, callbacked, *args, **kwargs):
        """
        real method executed when appender decorated with __init__ is called

        registry stores a set of values that is needed calling callbacked:
        callbacked - input strong - input weak - input on_call

        making weakref for all to prevent memory leak
        do not strongly store any objects that is not needed calling callbacked

        :param callbacked: to be called when calling is triggered
        :param kwargs: to be put input callbacked while calling
        :return:
        """
        # store args
        arr = ([], weakref.WeakValueDictionary(), {})
        self.__callback_funcs[callbacked] = arr
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

    def appender(self, _appender):
        """
        this is a decorator for callbacked append function

        decorate functions that append callbacked functions and
        kwargs to be put when calling callbacked afterward

        :param method: method for appending callbacked
        """
        return self.append

    def remove(self, method):
        """
        remove callbacked method

        :param method: method registered as a callbacked
        :return:
        """
        if method not in self.__callback_funcs:
            raise ValueError("given method doesnt exist in the register")
        self.__callback_funcs.pop(method)

    def remover(self, _remover):
        """
        decorator to decorate remover function

        :param _remover:
        :return:
        """
        return self.remove

    def enabler(self, _enabler):
        """
        decorator to decorate enabler function

        :param _enabler:
        :return:
        """
        return self.__enabler

    def __enabler(self, v):
        """
        real method executed when decorated enabler method called

        :param v:
        :return:
        """
        try:
            v = bool(v)
            self.__flag_enable = v
        except Exception as e:
            raise e

    def enable(self):
        """
        enable callback
        :return:
        """
        self.__flag_enable = True

    def disable(self):
        """
        disable callback
        :return:
        """
        self.__flag_enable = False


if __name__ == '__main__':
    # example

    class Foo:
        def __init__(self):
            pass

        @callbackRegistry
        def call_a_callback(self, **on_call_kwargs):
            print('caller')

        @call_a_callback.appender
        def append_a_callback(self, func, *args, **kwargs):
            print('appender')

        @call_a_callback.enabler
        def enable_a_callback(self, do_enable):
            print('enabler')

        @call_a_callback.remover
        def remove_a_callback(self, method):
            print('remover')


    f = Foo()


    class Weakrefable:
        pass


    def a_callback(arg0, arg1, arg2, *args, **kwargs):
        print(arg0, arg1, arg2)
        print(args)
        print(kwargs)


    a = Weakrefable()
    b = Weakrefable()

    f.append_a_callback(a_callback, 10, a, arg2=10, unknown_arg=b)
    # f.call_a_callback.disable()
    # f.enable_a_callback(True)
    # f.remove_a_callback(a_callback)
    f.call_a_callback(on_call=3.3)

    print(f.call_a_callback)

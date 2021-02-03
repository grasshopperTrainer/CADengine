import weakref as wr


class _FuncWrapper:
    def __init__(self, instance, func):
        self.__instance = wr.ref(instance)
        self.__func = wr.ref(func)

        self.__reset = True
        self.__cached_result = None

        self.__cached_args = []
        self.__cached_kwargs = {}

    def __call__(self, *args, **kwargs):
        if self.__reset or self.__is_args_new(*args, **kwargs):
            result = self.__func()(self.__instance(), *args, **kwargs)
            self.__cached_result = result
            self.__cache_args(args, kwargs)

            self.__reset = False
            return result
        else:
            return self.__cached_result

    # this hole concept of automatically checking args can become overhead
    def __cache_args(self, args, kwargs):
        """
        store kwargs

        :param args:
        :param kwargs:
        :return:
        """
        self.__cached_args = []
        self.__cached_kwargs = {}
        # make weak reference
        for a in args:
            if a is None or isinstance(a, (int, float, str, bool, list, tuple, set, dict)):
                self.__cached_args.append(a)
            else:
                self.__cached_args.append(wr.ref(a))
        for k, v in kwargs.items():
            if v is None or isinstance(v, (int, float, str, bool, list, tuple, set, dict)):
                self.__cached_kwargs[k] = v
            else:
                self.__cached_kwargs[k] = wr.ref(v)

    def __is_args_new(self, *args, **kwargs):
        """
        check if given args are new

        :param args:
        :param kwargs:
        :return:
        """
        # if input size is different
        if len(args) != len(self.__cached_args) or len(kwargs) != len(self.__cached_kwargs):
            return True
        # check args and kwargs
        for a, ca in zip(args, self.__cached_args):
            if a != (ca() if isinstance(ca, wr.ReferenceType) else ca):
                return True
        for k in kwargs:
            if k not in self.__cached_kwargs:
                return True
            a = self.__cached_kwargs[k]
            if kwargs[k] != (a() if isinstance(a, wr.ReferenceType) else a):
                return True
        return False

    def reset(self):
        self.__reset = True


class lazyFunc:
    """
    decorator
    decorated by this is lazy in three steps:
    1. In reset(initial state) state, execute decorated function and cache the returned, and return that value
    2. In cached state, does not execute the function but return cached.
    3. When reset, switch to reset state and go back to #1

    This is an additional interface, is needed
    1. to retrieve calling instance
    2. thus to enable explicit reset.
    """
    def __init__(self, func):
        self.__func = func
        self.__func_wrappers = wr.WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self.__func_wrappers.setdefault(instance, _FuncWrapper(instance, self.__func))

    def resetter(self, func):
        def __wrapper(instance):
            r = func()
            self.__func_wrappers[instance].reset
            return r
        return __wrapper


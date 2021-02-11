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


class lazyProp:
    """
    decorator
    same usage lazyFunc has
    """
    def __init__(self, func):
        self.__func = func
        self.__cache = wr.WeakKeyDictionary()
        self.__flags = wr.WeakKeyDictionary()

    def __get__(self, instance, owner):
        # init
        if instance not in self.__cache:
            # setattr(instance, f"_{owner.__name__.lstrip('_')}__lazyProp_{self.__func.__name__}", self)
            self.__flags[instance] = True
            self.__cache[instance] = None
        # recalc
        if self.__flags[instance]:
            self.__cache[instance] = self.__func(instance)
            self.__flags[instance] = False
        return self.__cache[instance]

    def __set__(self, instance, value):
        """
        reset cache switch

        :param instance:
        :param value: bool, set True to reset cache, False to disable gen. cache flag
        :return:
        """
        if not isinstance(value, bool):
            raise TypeError('use this interface to reset cache')
        if value:
            self.__flags[instance] = True
            self.__cache[instance] = None
        else:
            self.__flags[instance] = False

    # def reset(self, instance):
    #     """
    #     explicit cache reset accessed via '__lazyProp_{prop_name}' pattern
    #     :param instance:
    #     :return:
    #     """
    #     self.__flags[instance] = True

    def resetter(self, func):
        """
        decorator for cache reset

        reset to calculate
        :return:
        """
        def __wrapper(instance, *args, **kwargs):
            func(instance, *args, **kwargs)
            self.__flags[instance] = True
        return __wrapper

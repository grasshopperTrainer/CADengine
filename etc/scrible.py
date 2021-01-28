class FooType(type):
    def _foo_func(cls):
        return 'foo!'

    def _bar_func(cls):
        return 'bar!'

    def __getattr__(cls, key):
        if key == 'Foo':
            return cls._foo_func()
        elif key == 'Bar':
            return cls._bar_func()
        raise AttributeError(key)

    def __str__(cls):
        return 'custom str for %s' % (cls.__name__,)

class MyClass(metaclass=FooType):
    # __metaclass__ = FooType
    pass

# in python 3:
# class MyClass(metaclass=FooType):
#    pass


print(MyClass.Foo)
print(MyClass.Bar)
print(str(MyClass))
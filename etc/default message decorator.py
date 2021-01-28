


class A:
    log = ''
    def operation(func):
        def wrapper(self, *args, **kwargs):
            try:
                func(self, *args, **kwargs)
                self.log = 'operation success'
            except Exception as e:
                self.log = e
        return wrapper


    @operation
    def operate(self, a):
        if a == 1:
            raise

a = A()
a.operate(0)
print(a.log)
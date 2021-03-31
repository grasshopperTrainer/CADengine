
dd = 10
def a(obj):
    def wrapper():
        l = 10
        print(l)
        obj()
    return wrapper

@a
def kk():
    pass
print(kk)
kk()
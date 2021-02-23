import weakref

# can here be memory leak?
def Singleton(cls):
    instances = weakref.WeakKeyDictionary()

    def getinstance(*args):
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance

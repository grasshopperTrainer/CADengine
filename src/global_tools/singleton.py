def Singleton(cls):
    instances = {}

    def getinstance(*args):
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance

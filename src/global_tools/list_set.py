
class ListSet:
    """
    Simple list set combination for faster membership checking and iteration.

    Downside is that it implements list remove. Bad time complexity
    This problem could be resolved by implementing lazy removal but not yet needed.
    """

    def __init__(self):
        self.__list = []
        self.__set = set()
        self.__iter_idx = 0

    def __contains__(self, item):
        return item in self.__set

    def __len__(self):
        return self.__list.__len__()

    def __iter__(self):
        for i in self.__list:
            yield i

    def append(self, obj):
        self.__list.append(obj)
        self.__set.add(obj)

    def remove(self, obj):
        if obj not in self.__set:
            raise ValueError('obj not in ListSet')
        self.__list.remove(obj)
        self.__set.remove(obj)

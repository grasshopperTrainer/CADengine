import gkernel.dtype.geometric as gt
import threading


class ModelIterator:
    def __init__(self, shapes):
        self._shapes = shapes
        self._iter_idx = 0

    def __next__(self):
        for s in self._shapes:
            yield s

    def __iter__(self):
        return self


class Model:
    def __init__(self):
        self.__shapes = {}
        self.__plane = gt.Pln()
        self.__renderers = {}
        self.__Lock = threading.Lock()

    @property
    def lock(self):
        """
        User of threading has to take care of locking by himself
        :return: Lock,
        """
        return self.__Lock

    @property
    def plane(self):
        return self.__plane

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
    pass
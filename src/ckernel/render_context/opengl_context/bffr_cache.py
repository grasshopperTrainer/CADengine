import numpy as np
from collections import namedtuple


class ArrayContainer:
    """
    in case class can't become array itself
    """

    @property
    def array(self):
        return self.__array


class BffrCache(ArrayContainer):
    """
    ! vocabulary:
        point : vertex as geometric entity
        vertex: subarray that contains data per point. ex) coordinate, color
        block: consecutive number of vertex

    Interleaved array container that has some functionality of distributing sub arrays

    ! the class can not be ndarray subclass itself as it has to deal with size expansion.
    While expanding, the class has to swap its array to new ndarray and somehow post new
    array to `_Block` instance that has been viewing old array.
    """
    # initial size of array for placeholder

    def __init__(self, dtype, size):
        self.__array = np.ndarray(size, dtype=dtype)
        self.__array_len = size
        # for first fit allocation free space record, (idx, size)
        self.__block_pool = [(0, self.__array_len)]
        self.__blocks = []
        self.__num_vertex_inuse = 0

    def __getitem__(self, item):
        """
        for direct access into the array

        :param item:
        :return:
        """
        return self.__array.__getitem__(item)

    def __setitem__(self, key, value):
        self.__array.__setitem__(key, value)

    def __expand_array(self):
        """
        double the size of the array

        :return:
        """
        raise NotImplementedError

    def request_vacant(self, size):
        """
        :return: ndarray, consecutive vacant vertices from array of given size
        """
        block = self.__aloc_firstfit(size)
        self.__num_vertex_inuse += size
        return block

    def __aloc_firstfit(self, size):
        """
        check block pool linearly and if size is smaller then required, split the block are return requested
        not vary efficient, temporary implementation

        :param size:
        :return:
        """
        if size == 0:
            raise ValueError

        for i, (sidx, block_size) in enumerate(self.__block_pool):
            leftover = block_size - size
            if 0 <= leftover:
                if leftover == 0:
                    self.__block_pool.pop(i)
                else:
                    self.__block_pool[i] = (sidx+size, leftover)  # append new free space
                # TODO: think of memory freeing mechanism
                block = self.__Block(self, sidx, sidx+size)
                self.__blocks.append(block)
                return block

        raise NotImplementedError('overflow')

    def __set_idx_vacant(self, idx):
        """
        ! block of returned idx can be overridden at any time

        When block is not used anymore it can be returned to be reused.
        But how to check not-used is yet unknown.
        :param idx: int, returned block index
        :return:
        """
        if idx == self.__block_vacant_pointer-1:
            self.__block_vacant_pointer -= 1
        else:
            self.__block_returned.register(idx)

    @property
    def array(self):
        """
        :return:
        """
        return self.__array

    @property
    def bytesize(self):
        """
        size of whole array in bytes

        :return:
        """
        return self.__array.size * self.__array.itemsize

    @property
    def num_used_vrtx(self):
        """

        :return: int, number of vertex in use
        """
        return self.__num_vertex_inuse

    @property
    def field_props(self):
        """
        set of property describing interleaveness of the array

        :return: list(namedtuple(name, shape, dtype, stride),...)
        """
        tuples = []
        ntuple = namedtuple('interleave_prop', 'name, size, dtype, stride, offset')
        stride = self.array.itemsize
        for name, (dtype, offset) in self.__array.dtype.fields.items():
            dtype, shape = dtype.subdtype
            tuples.append(ntuple(name, shape, dtype, stride, offset))
        return tuple(tuples)

    @classmethod
    def from_array(cls, array):
        """
        create buffer from raw ndarray

        :param array: ndarray, array to comprehend as a cpu buffer
        :return:
        """
        raise NotImplementedError

    class __Block:
        """
        redirector to buffer array

        Syncs value update between sliced array and master array
        """

        def __init__(self, array_container, start_idx, stop_idx):
            self.__array_container = array_container
            self.__start = start_idx
            self.__stop = stop_idx

        def __getitem__(self, item):
            """
            slice is used to update value of the array

            Updated value always has to be push into container's array.
            :param item:
            :return:
            """
            return self.__array_container.array[self.__start:self.__stop].__getitem__(item)

        def __str__(self):
            return f"<Block [{self.__start}:{self.__stop}]>"

        @property
        def block_loc(self):
            """
            block location in raw array

            :return: tuple, (start index, block size)
            """
            return self.__start, self.__stop
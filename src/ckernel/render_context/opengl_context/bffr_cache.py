import numpy as np
from collections import namedtuple
from .translators import npdtype_to_gldtype


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

    def __init__(self, dtype, locs, size=32):
        # extra location data
        if not isinstance(locs, (list, tuple)):
            raise TypeError
        if len(locs) != len(dtype.fields):
            raise ValueError('each field has to have location values')
        self.__locs = {n:l for n, l in zip(dtype.fields, locs)}

        self.__array = np.ndarray(size, dtype=dtype)
        # for first fit allocation free space record, (idx, size)
        self.__block_pool = [(0, len(self.__array))]
        self.__block_inuse = set()
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

    def __len__(self):
        return len(self.__array)

    def __expand_array(self):
        """
        double the size of the array

        :return:
        """
        raise NotImplementedError

    def request_block(self, size):
        """
        :return: ndarray, consecutive vacant vertices from array of given size
        """
        block = self.__aloc_firstfit(size)
        self.__num_vertex_inuse += size
        return block

    def _release_block(self, block, reset_val=None):
        """
        return block, release ownership of subarray

        ! block of returned idx can be overridden at any time
        :param block: block to release ownership
        :param reset_val: value to fill released block with
        :return:
        """
        if block not in self.__block_inuse:
            raise ValueError('block not of this cache, please access via block.release()')
        self.__block_inuse.remove(block)
        # add into pool, is there good way of merging pools?
        s, e = None, None
        for i in sorted(block.indices):
            # fill released value with reset_val
            if reset_val is not None:
                self.array[i] = reset_val

            if s is None:
                s, e = i, i
            elif i == e+1:
                e = i
            else:   # reset consecutive
                self.__block_pool.append((s, e-s+1))    # start, size
                s, e = i
        self.__block_pool.append((s, e-s+1))            # dont forget remaining
        # count vertex in use
        self.__num_vertex_inuse -= len(block.indices)

    def __aloc_firstfit(self, size):
        """
        check block pool linearly and if size is smaller then required, split the block are return requested
        not vary efficient, temporary implementation

        :param size:
        :return:
        """
        if size == 0:
            raise ValueError

        # find vacant indices
        indices = []
        while self.__block_pool:
            sidx, block_size = self.__block_pool[-1]
            leftover = block_size - size
            if 0 <= leftover:
                if leftover == 0: # all taken
                    self.__block_pool.pop(-1)
                else:   # some left
                    self.__block_pool[-1] = (sidx+size, leftover)  # append new free space
                indices = list(range(sidx, sidx+size))
                break
            else:   # take all of current and continue searching
                self.__block_pool.pop(-1)
                indices += list(range(sidx, sidx+size))

        if len(indices) != size:
            raise NotImplementedError('overflow')

        block = self.__Block(self, indices)
        self.__block_inuse.add(block)
        return block

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
    def gldtype(self):
        return npdtype_to_gldtype(self.__array.dtype)

    @property
    def num_vrtx_inuse(self):
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
        ntuple = namedtuple('interleave_prop', 'name, loc, size, dtype, stride, offset')
        stride = self.array.itemsize
        for name, (dtype, offset) in self.__array.dtype.fields.items():
            dtype, shape = dtype.subdtype
            loc = self.__locs[name]
            tuples.append(ntuple(name, loc, shape, dtype, stride, offset))
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

        def __init__(self, array_container, indices):
            self.__cache = array_container
            self.__indices = indices

        def __getitem__(self, item):
            """
            slice is used to update value of the array

            Updated value always has to be push into container's array.
            :param item:
            :return:
            """
            return self.__cache.array[item][tuple(self.__indices)]

        def __setitem__(self, key, value):
            self.__cache.array[key][self.__indices] = value

        def __str__(self):
            return f"<Block {self.__indices}]>"

        @property
        def indices(self):
            """
            :return: tuple of array indices
            """
            return tuple(self.__indices)

        @property
        def arr(self):
            """
            debug access
            :return:
            """
            return self.__cache.array

        def release(self, reset_val=None):
            """
            end of usage, release memory

            :param reset_val: value to fill released block with
            :return:
            """
            self.__cache._release_block(self, reset_val)
            self.__cache = None
            self.__indices = None
import numpy as np
from collections import namedtuple
import heapq

from .translators import npdtype_to_gldtype
from global_tools.skip_list import SkipList

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

    def __init__(self, dtype, locs, size=4):
        # extra location data
        if not isinstance(locs, (list, tuple)):
            raise TypeError
        if len(locs) != len(dtype.fields):
            raise ValueError('each field has to have location values')
        self.__locs = {n: l for n, l in zip(dtype.fields, locs)}
        self.__array = np.ndarray(size, dtype=dtype)
        # for first fit allocation free space record,
        self.__block_pool = [(0, len(self.__array))]    # (start, stop) min heap
        self.__block_inuse = SkipList(key_provider=lambda x: x.indices[-1])
        self.__num_vertex_inuse = 0
        self.__highest_indx = -1

    def __getitem__(self, item):
        """
        for direct access into the array

        :param item:
        :return:
        """
        return self.__array.__getitem__(item)

    def __setitem__(self, key, value):
        raise Exception('dont do this, access via block or `fill_array`')
        # self.__array.__setitem__(key, value)

    def __len__(self):
        return len(self.__array)

    def __str__(self):
        return f"<BffrCache {tuple(ps[0] for ps in self.field_props)}>"

    def __expand_array(self):
        """
        in case of overflow double the size of the array

        :return:
        """
        old_len = len(self.__array)
        new_len = old_len * 2
        new_arr = np.ndarray(shape=new_len, dtype=self.__array.dtype)
        new_arr[:old_len] = self.__array
        self.__block_pool.append((old_len, new_len))
        self.__array = new_arr

    def fill_array(self, v):
        """
        fill array with given value

        ! be aware that this function doesn't mark byte as active
        :param v:
        :return:
        """
        self.__array[:] = v

    @property
    def active_size(self):
        """
        size of array in use

        ! this doesnt mean given size is tightly packed
        :return: None or int
        """
        return self.__highest_indx + 1

    def request_block(self, size):
        """
        get subarray not in use

        ! returned block is guaranteed to fill in buffer holes from the front
        :return: __Block, consecutive vacant vertices from array of given size
        """
        if size == 0:
            raise ValueError

        # find vacant indices
        indices = []
        while 0 < size:
            if not self.__block_pool:
                self.__expand_array()

            s, e = self.__block_pool[0]
            vacant_size = e - s
            indices += list(range(s, min(e, s + size)))  # take as much as possible
            if vacant_size <= size:  # vacant is fully taken
                heapq.heappop(self.__block_pool)  # remove
            else:  # vacant is partially taken
                self.__block_pool[0] = (s + size, e)  # simply replace
            size -= vacant_size

        block = self.__Block(self, indices)
        self.__block_inuse.push(block) # pushing into skip list
        # update blocks inuse size
        self.__num_vertex_inuse += len(indices)
        self.__highest_indx = max(self.__highest_indx, indices[-1])
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
        # stop tracking
        self.__block_inuse.remove(block)

        # return into pool
        s, e = None, None
        for i in block.indices:  # if not modified illegally, indices are already sorted
            # fill released with reset_val
            if reset_val is not None:
                self.array[i] = reset_val
            # compact consecutive
            if s is None:
                s = e = i
            elif i == e + 1:
                e = i
            else:  # consecutive finish, wrap as a block
                heapq.heappush(self.__block_pool, (s, e+1))  # start, stop
                s = e = i  # start counting new consecutive
        heapq.heappush(self.__block_pool, (s, e+1))  # dont forget remaining
        # count vertex in use
        self.__num_vertex_inuse -= block.size
        # update highest index
        if block.indices[-1] == self.__highest_indx:
            if self.__block_inuse:
                self.__highest_indx = self.__block_inuse[-1].high_indx
            else:
                self.__highest_indx = -1    # 0 size

    def refill_foremost(self, reset_val=None):
        """
        fill foremost gap by allocating latest block inuse

        ! this changes the arrangement of the cache.
        Rearranging relationship between cache data of specific location and other objects viewing
        that location is totally obligatory to the caller of this method.
        :param reset_val: value to fill into released vertex
        :return: mapping info tuple((from indices...), (to indices...))
        """

        # size can differ, last can be bigger than to fill and smaller or equal
        if self.__block_pool[0][0] < self.active_size:  # cant be equal
            src_block = self.__block_inuse[-1]
            self._release_block(src_block)
            src_idxs = src_block.indices
            src_size = len(src_idxs)
            # collect indicies
            trg_idxs = []
            while True:
                start, stop = self.__block_pool[0]
                left = src_size - (stop - start)
                if 0 <= left:   # fully taken or need more
                    heapq.heappop(self.__block_pool)
                    trg_idxs += list(range(start, stop))
                else:   # underflow
                    self.__block_pool[0] = (start+src_size, stop)
                    trg_idxs = list(range(start, start+src_size))
                if left <= 0:
                    break
            # copy data, reset released, and reset indices
            self.__array[trg_idxs] = self.__array[list(src_idxs)]
            if reset_val:
                self.__array[src_idxs] = reset_val
            setattr(src_block, f"_{src_block.__class__.__name__[2:]}__indices", trg_idxs)   # bad hidden access
            # relocated source block with new indices
            self.__block_inuse.push(src_block)
            if self.__block_inuse:
                self.__highest_indx = self.__block_inuse[-1].high_indx
            else:
                self.__highest_indx = -1

            return tuple(src_idxs), tuple(trg_idxs)

    @property
    def array(self):
        """
        :return:
        """
        return self.__array

    @property
    def active_bytesize(self):
        """
        size of whole array in bytes

        :return:
        """
        return self.active_size * self.__array.itemsize

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
            self.__indices = list(indices)

        def __getitem__(self, item):
            """
            slice is used to update value of the array

            Updated value always has to be push into container's array.
            :param item:
            :return:
            """
            return self.__cache.array[item][self.__indices]

        def __setitem__(self, key, value):
            """
            ex) block['vtx'] = 10, 10, 10, 1

            :param key:
            :param value:
            :return:
            """
            # for 1D setitem
            if not isinstance(key, tuple):
                self.__cache.array[key][self.__indices] = value
            else:
                self.__cache.array[key[0]][self.__indices[key[1]]] = value

        def __len__(self):
            return len(self.__indices)

        def __str__(self):
            return f"<Block {self.__indices}]>"
        @property
        def indices(self):
            """
            :return: tuple of array indices
            """
            return tuple(self.__indices)
        #
        # @property
        # def size(self):
        #     return len(self.__indices)

        @property
        def high_indx(self):
            """
            biggest index of blocks' indices

            :return:
            """
            return self.__indices[-1]

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
            # ! resetting has to be below
            self.__cache = None
            self.__indices = None

        def release_refill(self, reset_val=None):
            """
            release and refill consecutively as a set op operation

            ! This doesn't guarantee that released vertex will be filled.
            It is guaranteed that foremost will be filled using lastest Block

            :param reset_val: value to fill into released vertex by releasing and refilling
            :return:
            """
            self.__cache._release_block(self, reset_val)
            mapping = self.__cache.refill_foremost(reset_val)
            self.__cache = None
            self.__indices = None
            return mapping

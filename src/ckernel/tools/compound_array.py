import numpy as np
import weakref


class CompoundArray:
    """
    Interleaved array that has some functionality of distributing sub arrays
    """
    # initial size of array for placeholder
    __ARRAY_INIT_SIZE = 32

    def __init__(self, dtype):
        """
        create master array
        :param dtype: structured dtype
        """
        # create master array
        try:
            self.__dtype = np.dtype(dtype)
        except:
            raise Exception('cant interprete given dtype description into numpy dtype')
        else:
            self.__array = np.ndarray(self.__ARRAY_INIT_SIZE, dtype=dtype)
        self.__array_len = self.__ARRAY_INIT_SIZE
        # for first fit allocation free space record, (idx, size)
        self.__block_pool = [(0, self.__array_len)]

    def __expand_array(self):
        """
        double the size of the array

        :return:
        """
        raise NotImplementedError

    def request_block_vacant(self, size):
        """
        :return: ndarray, consecutive vacant vertices from array of given size
        """
        return self.__aloc_firstfit(size)

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
                return self.__Block(self.__array, sidx, size)
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
            self.__block_returned.append(idx)

    class __Block(np.ndarray):
        """
        Block array subclass
        needed to store index value used to free master array when returned
        """
        def __new__(cls, raw_arr, sidx, size):
            """

            :param raw_arr: array to slice from
            :param sidx: start index
            :param size: size of block
            """
            obj = raw_arr[sidx: sidx + size].view(cls)
            # maybe better store weak arr
            obj.__block_loc = (sidx, size)
            return obj

        @property
        def block_loc(self):
            """
            block location in raw array

            :return: tuple, (start index, block size)
            """
            return self.__block_loc

    @property
    def array(self):
        """
        debug use only!
        :return:
        """
        return self.__array


# class BffrAttrDescriptor:
#     """
#     manage updating block value of master array
#     problem is context dependency has to be delt here...
#     """
#     class __BlockContainer:
#         def __init__(self, block, viewer):
#             """
#             Maintain exposed data to prohibit external manipulation of array
#
#             :param block:
#             """
#             self.__block = block    # sub array of master array
#             self.__viewer = viewer
#             if self.__block.shape == (4, ):
#                 self.__edata = self.__block.copy().reshape(4, 1).view(self.__viewer)
#             else:
#                 self.__edata = self.__block.copy().T.view(self.__viewer)
#
#         def update_value(self, value):
#             if not (isinstance(value, np.ndarray) and self.__edata.shape == value.shape):
#                 raise ValueError
#             self.__block[:] = value
#             self.__edata[:] = value
#
#         @property
#         def value(self):
#             return self.__edata
#
#     def __init__(self, struct, field_name, viewer=np.ndarray):
#         self.__idict = weakref.WeakKeyDictionary()  # instance dict
#         self.__struct = struct                      # master array
#         self.__field_name = field_name              # field of struct
#         self.__viewer = viewer                      # ndarray subclass for block, viewing struct
#
#     def __get__(self, instance, owner):
#         """
#         :param instance:
#         :param owner:
#         :return:
#         """
#         if instance not in self.__idict:
#             self.__idict[instance] = self.__BlockContainer(self.__get_new_block(), self.__viewer)
#         return self.__idict[instance].value
#
#     def __set__(self, instance, value):
#         """
#         update block value
#
#         :param instance:
#         :param value:
#         :return:
#         """
#         self.__idict[instance].update_value(value)
#
#     def __get_new_block(self):
#         """
#         get new block from array and make exposed view data
#
#         :return:
#         """
#         return self.__struct.request_block_vacant()[self.__field_name]
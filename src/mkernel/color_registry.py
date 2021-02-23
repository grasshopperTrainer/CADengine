import threading
import random
import weakref as wr
from global_tools.singleton import Singleton
import numpy as np


@Singleton
class GlobalColorRegistry:
    """
    to provide cid for all shapes

    ! has to be thread safe
    """
    def __init__(self):
        self.__record = wr.WeakKeyDictionary()

        self.__color_comp_bitsize = 8
        self.__color_comp_bitmask = [0 for _ in range(3)]
        self.__lock = threading.Lock()

    def register_get(self, entity):
        """
        register color id with the entity

        ! thread safe
        :param entity:
        :return: cid
        """
        with self.__lock:
            if entity in self.__record:
                return _ColorGetter(self.__record[entity])
            # find vacant color
            while True:
                color = np.random.randint(low=0, high=256, size=3, dtype=np.ubyte)
                # check for reserved 0
                if (color == 0).all():
                    continue

                masked_count = 0
                for bm, cc in zip(self.__color_comp_bitmask, color):
                    if bm & (1 << cc):
                        masked_count += 1
                # color is already occupied
                if masked_count == 3:
                    continue
                else:  # mask
                    for i in range(3):
                        self.__color_comp_bitmask[i] |= color[i]
                    break
            self.__record[entity] = color
            return _ColorGetter(color)

    def deregister(self, entity):
        """
        remove entity from the register

        :param entity:
        :return:
        """
        with self.__lock:
            if entity not in self.__record:
                raise
            raise NotImplementedError

    def is_registered(self, entity):
        """
        check if entity is registered

        :param entity:
        :return:
        """
        return entity in self.__record


class _ColorGetter:
    def __init__(self, color):
        self.__color = color

    def asfloat(self):
        return self.__color/255

    def asubyte(self):
        return self.__color.aslist()

    def ashex(self):
        raise NotImplementedError
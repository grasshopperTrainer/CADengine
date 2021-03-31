import threading
import random
import weakref as wr
from global_tools.singleton import Singleton
import numpy as np
from gkernel.color import ClrRGBA


@Singleton
class GlobalColorRegistry:
    """
    to provide cid for all shapes

    ! has to be thread safe
    """
    def __init__(self):
        self.__entity_color = {}
        self.__color_entity = wr.WeakValueDictionary()

        self.__color_comp_bitsize = 8
        self.__color_comp_bitmask = [0 for _ in range(3)]
        self.__lock = threading.Lock()

    def register_entity(self, entity):
        """
        register color id with the entity

        ! thread safe
        :param entity:
        :return: cid
        """
        with self.__lock:
            if entity in self.__entity_color:
                return _ColorGetter(self.__entity_color[entity])
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

            tcolor = tuple(color)
            self.__entity_color[entity] = tcolor
            self.__color_entity[tcolor] = entity
            return _ColorGetter(color)

    def deregister(self, entity):
        """
        remove entity from the register

        :param entity:
        :return:
        """
        with self.__lock:
            if entity not in self.__entity_color:
                raise
            raise NotImplementedError

    def is_registered(self, entity):
        """
        check if entity is registered

        :param entity:
        :return:
        """
        return entity in self.__entity_color

    def get_registered(self, cid):
        """
        return entity if given cid is valid

        :param cid: (int, int, int) tuple of 3 ubyte-like values
        :return:
        """
        return self.__color_entity.get(cid, None)


class _ColorGetter:
    def __init__(self, color):
        self.__color = color

    def asfloat(self):
        return self.__color/255

    def asubyte(self):
        return self.__color.aslist()

    def ashex(self):
        raise NotImplementedError
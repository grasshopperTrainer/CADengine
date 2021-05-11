import threading
import random
import weakref as wr
from global_tools.singleton import Singleton
import numpy as np

from gkernel.color import ClrRGBA

# 'GL_RGB10_A2UI', 10 bits for each RGB
# can be expanded in farther implementation
_BITDEPTH = 30
_COMP_BITDEPTH = 10
_COMP_BITMAX = 2**_COMP_BITDEPTH - 1

@Singleton
class GIDP:
    """
    Global ID Provider
    to provide oid for all shapes

    ! has to be thread safe
    """

    def __init__(self):
        self.__entity_goid = wr.WeakKeyDictionary()
        self.__goid_entity = wr.WeakValueDictionary()

        self.__lock = threading.Lock()

    def register_entity(self, entity):
        """
        register color id with the entity

        ! thread safe
        :param entity:
        :return: oid
        """

        with self.__lock:
            if entity in self.__entity_goid:
                return self.__entity_goid[entity]

            # find vacant id
            while True:
                goid = random.getrandbits(_BITDEPTH)
                if goid not in self.__goid_entity:
                    break

            goid = GOID(goid)
            self.__entity_goid[entity] = goid
            self.__goid_entity[goid] = entity
            return goid

    def deregister(self, entity):
        """
        remove entity from the register

        :param entity:
        :return:
        """
        with self.__lock:
            if entity not in self.__entity_goid:
                raise
            goid = self.__entity_goid[entity]
            del self.__entity_goid[entity]
            del self.__goid_entity[goid]

    def is_registered(self, entity):
        """
        check if entity is registered

        :param entity:
        :return:
        """
        return entity in self.__entity_id

    def get_registered(self, goid):
        """
        return entity if given goid object

        :param goid: _GOID
        :return:
        """
        with self.__lock:
            return self.__goid_entity.get(goid, None)

    def get_registered_byvalue(self, value):
        if isinstance(value, int):
            return self.get_registered(GOID(value))
        elif isinstance(value, (np.ndarray, tuple, list)):
            return self.get_registered(GOID.from_array(value))
        raise NotImplementedError


class GOID:
    """
    Global Object IDentifier
    """

    @classmethod
    def from_array(cls, arr):
        """
        derive GOID raw integer value from array

        :param arr:
        :return:
        """
        if isinstance(arr, np.ndarray):
            if len(arr) == 3 and arr.dtype == np.dtype('uint'):
                bitmap = ''.join([bin(v)[2:].rjust(_COMP_BITDEPTH, '0')[:_COMP_BITDEPTH] for v in arr])
                return cls(int(bitmap, 2))
        elif len(arr) == 3 and isinstance(arr, bytes):
            bitmap = ''.join([bin(v)[2:].rjust(_COMP_BITDEPTH, '0')[:_COMP_BITDEPTH] for v in arr])
            return cls(int(bitmap, 2))
        raise NotImplementedError

    def __init__(self, raw):
        self.__raw = raw

    def __str__(self):
        return f"<GOID {self.__raw}>"

    def __hash__(self):
        return hash(self.__raw)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def as_raw(self):
        """
        :return: raw id as unsigned int
        """
        return self.__raw

    def __get_color_bits(self):
        """
        translate goid's raw int expression into binary rgb color components
        :return: (r, g, b) binary expression
        """
        # bits
        bits = bin(self.__raw)[2:].rjust(_BITDEPTH, '0')
        color = []

        # color component bit depth
        cbits = _BITDEPTH // 3
        for i in range(3):
            comp = bits[i * cbits:(i + 1) * cbits]
            color.append(comp)
        return color

    # def as_rgb_uint(self):
    #     return np.array([int(c, 2) for c in self.__get_color_bits()], dtype='uint32')
    def as_rgb_float(self):
        return np.array([int(c, 2)/_COMP_BITMAX for c in self.__get_color_bits()], dtype='float')


if __name__ == '__main__':
    a = GOID(5, 8)
    print(a == 5)
    s = {a}
    print(5 in s)
    print(np.array([1, 2, 3], dtype='uint128').dtype)

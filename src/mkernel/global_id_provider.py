import threading
import random
import weakref as wr
from global_tools.singleton import Singleton
import numpy as np
from gkernel.color import ClrRGBA


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

        self.__bitdepth = 32

        self.__lock = threading.Lock()

    def register_entity(self, entity, color_comp_sig=None):
        """
        register color id with the entity

        ! thread safe
        :param entity:
        :param color_comp_sig:
        :return: oid
        """
        if color_comp_sig is None:
            ccomp_sig = 'rgb'
        else:
            raise NotImplementedError

        with self.__lock:
            if entity in self.__entity_goid:
                return self.__entity_goid[entity]

            # find vacant id
            while True:
                goid = random.getrandbits(self.__bitdepth)
                if goid not in self.__goid_entity:
                    break

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
            return self.__goid_entity.get(int(goid), None)

    # def get_registered_byvalue(self, val):
    #     """
    #
    #     :return:
    #     """
    #     if isinstance(val, np.ndarray):
    #         if val.dtype == 'ubyte':
    #             goid = int(''.join(bin(v)[2:].rjust(8, '0') for v in val), 2)
    #             goid = GOID(goid, 'rgb', 8)
    #         elif val.dtype == 'uint':
    #             print(val, val.dtype)
    #             raise
    #         return self.__goid_entity.get(goid, None)
    #     else:
    #         raise NotImplementedError


# class GOID:
#     """
#     Global Object IDentifier
#     """
#
#     def __init__(self, oid, components, bitdepth):
#         self.__raw = oid
#         self.__components = components
#         self.__bitdepth = bitdepth
#
#     def __str__(self):
#         return f"<GOID {self.__raw}>"
#
#     def __hash__(self):
#         return hash(self.__raw)
#
#     def __eq__(self, other):
#         return hash(self) == hash(other)
#
#     def as_int(self):
#         """
#         :return: raw id as unsigned int
#         """
#         return self.__raw
#
#     def as_rgb_float(self):
#         """
#         :return: tuple, rgb value in float range (0 ~ max color component value)
#         """
#         cmax = 2 ** self.__bitdepth - 1
#         oid = self.as_rgb_unsigned()
#         return tuple(c / cmax for c in oid)
#
#     def as_rgba_float(self):
#         if self.__components == 'rgb':
#             return *self.as_rgb_float(), 1
#         else:
#             raise NotImplementedError
#
#     def as_rgb_unsigned(self):
#         """
#         :return: tuple, rgb as unsigned value
#         """
#         color_bits = bin(self.__raw)[2:].rjust(self.__bitdepth * 3, '0')
#         oid = tuple(int(color_bits[i * self.__bitdepth:(i + 1) * self.__bitdepth], 2) for i in range(3))
#         return oid
#
#     def ashex(self):
#         raise NotImplementedError

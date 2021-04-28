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
        self.__entity_oid = wr.WeakKeyDictionary()
        self.__oid_entity = wr.WeakValueDictionary()

        # color component bit size
        self.__ccomp_bsize = 8
        # oid is rgb conversion compatible, so whole id space is =
        self.__oid_range = 1, 2 ** (self.__ccomp_bsize * 3)

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
            if entity in self.__entity_oid:
                return _OIDConverter(self.__entity_oid[entity])

            # find vacant id
            while True:
                oid = random.randint(*self.__oid_range)
                if oid not in self.__oid_entity:
                    break

            # converto into color
            self.__entity_oid[entity] = oid
            self.__oid_entity[oid] = entity
            return _OIDConverter(oid, ccomp_sig, self.__ccomp_bsize)

    def deregister(self, entity):
        """
        remove entity from the register

        :param entity:
        :return:
        """
        with self.__lock:
            if entity not in self.__entity_oid:
                raise
            oid = self.__entity_oid[entity]
            del self.__entity_oid[entity]
            del self.__oid_entity[oid]

    def is_registered(self, entity):
        """
        check if entity is registered

        :param entity:
        :return:
        """
        return entity in self.__entity_id

    def get_registered(self, oid):
        """
        return entity if given oid is valid

        :param oid: (int, int, int) tuple of 3 ubyte-like values
        :return:
        """
        # maybe need to separate?
        # normalize oid
        if not isinstance(oid, int):
            if isinstance(oid, (tuple, list)) and len(oid) == 3:
                if all(isinstance(c, float) for c in oid):
                    cmax = 2 ** self.__ccomp_bsize - 1
                    oid = [int(cmax*c) for c in oid]
                elif all(isinstance(c, int) for c in oid):
                    pass
                else:
                    raise ValueError
                oid = int(''.join(bin(c)[2:].rjust(self.__ccomp_bsize, '0') for c in oid), 2)
            else:
                raise ValueError

        with self.__lock:
            return self.__oid_entity.get(oid, None)


class _OIDConverter:
    """
    Converts id into required form
    """

    def __init__(self, oid, ccomp_sig, ccomp_bsize):
        self.__oid = oid
        self.__ccomp_sig = ccomp_sig
        self.__ccomp_bsize = ccomp_bsize

    def asint(self):
        """
        :return: raw id as unsigned int
        """
        return self.__oid

    def as_rgb_float(self):
        """
        :return: tuple, rgb value in float range (0 ~ max color component value)
        """
        cmax = 2 ** self.__ccomp_bsize - 1
        oid = self.as_rgb_unsigned()
        return tuple(c / cmax for c in oid)

    def as_rgba_float(self):
        if self.__ccomp_sig == 'rgb':
            return *self.as_rgb_float(), 1
        else:
            raise NotImplementedError

    def as_rgb_unsigned(self):
        """
        :return: tuple, rgb as unsigned value
        """
        color_bits = bin(self.__oid)[2:].rjust(self.__ccomp_bsize * 3, '0')
        oid = tuple(int(color_bits[i * self.__ccomp_bsize:(i + 1) * self.__ccomp_bsize], 2) for i in range(3))
        return oid

    def ashex(self):
        raise NotImplementedError

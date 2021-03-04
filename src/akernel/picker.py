import gkernel.dtype.geometric as gt
from gkernel.constants import ATOL
import numpy as np
from numbers import Number


class InitPosPicker:
    """
    sketchup style initial pos picker
    """

    def __init__(self, offset: Number, zlimit=None):
        """

        :param offset: selection plane offset from camera xy pos
                       this is used to place selection ahead camera position
        :param xlimit: constraint to pick only position of positive x
        :param ylimit: constraint to pick only position of positive y
        :param zlimit: constraint to pick only position of positive z
        """
        self.__offset = offset
        self.__limits = [lambda _: True] * 3

        if zlimit is None:
            self.__limits[2] = lambda z: bool(np.isclose(z, 0, atol=ATOL) or z > 0)

    def pick(self, camera, screen_coord):
        """

        :param camera: camera object
        :param screen_coord: screen xy coord in (.0 ~ .1)
        :return: (plane_key, intersection point)
        """

        # 1. find cursor ray
        # 2. find selection plane
        # 3. find intersection with camera offsetted plane
        #   1) camera offseted plane
        #   2) intsersection

        R = camera.frusrum_ray(*screen_coord).as_vec()

        adeq_plns = sorted([(gt.Vec.cross(R, x).length, k) for k, x in zip(('x', 'y', 'z'), gt.Pln().axes)])
        cam_pln = camera.tripod.plane
        proj_ori = gt.Vec(*cam_pln.origin.xy, 0)
        off_vec = -cam_pln.axis_z.projected_on_xy().normalize() * self.__offset
        off_pln = gt.Pln((proj_ori + off_vec).xyz, (1, 0, 0), (0, 1, 0), (0, 0, 1))

        # finding intersection
        # 0 origin, t amplifier, R, ray vector, P intersection point
        # O + t*R = P
        O = cam_pln.origin
        for _, key in adeq_plns:
            Px, Ox, Rx = (getattr(i, key) for i in (off_pln.origin, O, R))
            t = (Px - Ox) / Rx
            P = O + t * R

            for l, comp in zip(self.__limits, P.xyz):
                if not l(comp):
                    break
            else:  # not broken - all limit passed
                return 'xyz'.replace(key, ''), P

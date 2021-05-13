import gkernel.dtype.geometric as gt
from gkernel.constants import ATOL
import numpy as np
from numbers import Number


class VicinityPicker:
    """
    sketchup style initial pos picker
    """

    def __init__(self):
        self.__constraints = [lambda x: True] * 3
        # do not pick below z 0
        self.__constraints[2] = lambda z: bool(np.isclose(z, 0, atol=ATOL) or z > 0)

    def pick(self, plane: gt.Pln, camera, cursor):
        """
        pick plane frustum ray intersection

        :param camera:
        :param cursor:
        :return: (axis idx, intersectpoint)
        """

        R = camera.frusrum_ray(*cursor.pos_local.xy).as_vec()
        adequacy = sorted([(gt.Vec.cross(R, x).length, k) for k, x in zip(range(3), plane.axes)])

        # finding intersection
        # 0 origin, t amplifier, R, ray vector, P intersection point
        # O + t*R = P
        cam_pln = camera.tripod.plane
        O = cam_pln.origin
        for _, idx in adequacy:
            Px, Ox, Rx = (getattr(i, ('x', 'y', 'z')[idx]) for i in (plane.origin, O, R))
            t = (Px - Ox) / Rx
            P = O + t * R

            for l, comp in zip(self.__constraints, P.xyz):
                if not l(comp):
                    break
            else:  # not broken - all limit passed
                return idx, P
        return None, None

    def pick_camera_relative(self, camera, cursor, offset):
        """
        pick relative position against camera from camera

        :param offset: selection plane offset from camera xy pos
                       this is used to place selection ahead camera position
        :param camera: Camera,
        :param cursor: Curosr,
        :return: (plane_key, intersection point)
        """

        # 1. find cursor ray
        # 2. find selection plane
        # 3. find intersection with camera offsetted plane
        #   1) camera offseted plane
        #   2) intsersection
        coord = cursor.pos_local.xy
        R = camera.frusrum_ray(*coord).as_vec()

        adeq_plns = sorted([(gt.Vec.cross(R, x).length, k) for k, x in zip(('x', 'y', 'z'), gt.Pln().axes)])
        cam_pln = camera.tripod.plane
        proj_ori = gt.Vec(*cam_pln.origin.xy, 0)
        off_vec = -cam_pln.axis_z.project_on_xy().normalize() * offset
        off_pln = gt.Pln((proj_ori + off_vec).xyz, (1, 0, 0), (0, 1, 0), (0, 0, 1))

        # finding intersection
        # 0 origin, t amplifier, R, ray vector, P intersection point
        # O + t*R = P
        O = cam_pln.origin
        for _, key in adeq_plns:
            Px, Ox, Rx = (getattr(i, key) for i in (off_pln.origin, O, R))
            t = (Px - Ox) / Rx
            P = O + t * R

            for l, comp in zip(self.__constraints, P.xyz):
                if not l(comp):
                    break
            else:  # not broken - all limit passed
                return 'xyz'.replace(key, ''), P

import gkernel.dtype.geometric as gt
from gkernel.constants import ATOL
import numpy as np
from numbers import Number


class AxisPicker:
    """
    sketchup style axis picker
    """

    def __init__(self):
        pass

    def pick(self, ray: gt.Ray, pln: gt.Pln):
        """
        :param ray: Ray, frustum ray
        :param pln: Pln, plane with reference point and axes to measure
        :return: (plane_key, intersection point)
        """
        distances = []
        for k, axis in zip('xyz', pln.axes):
            av = axis
            bv = ray.as_vec()

            cv = ray.origin - pln.origin
            v0 = gt.Vec.cross(av, bv)
            v1 = gt.Vec.cross(cv, bv)
            # intersection points
            t = gt.Vec.dot(v1, v0) / (v0.length ** 2)
            p0 = pln.origin + av * t
            s = gt.Vec.dot(bv, p0 - ray.origin) / (bv.length ** 2)
            p1 = ray.origin + bv * s

            distances.append(((p0 - p1).length, p0, k))
        distances.sort(key=lambda x: x[0])
        return distances[0]

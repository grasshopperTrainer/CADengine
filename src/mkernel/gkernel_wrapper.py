from .shape import Shape
import gkernel.dtype.geometric.primitive as pg
import numpy as np

def is_zero(v):
    """
    checking zero with min value threshold
    :param v: value to check
    :return:
    """
    if abs(v) > pg.ATOL:
        return False
    return True


class Ray(pg.Ray, Shape):
    pass


class Pnt(pg.Pnt, Shape):

    @classmethod
    def is_point_like(cls, *points):
        """
        check if given iterable can be interpreted as point coordinate
        :param points: iterable describing coordinate
        :return:
        """
        for p in points:
            if isinstance(p, (list, tuple)) & len(p) == 3:
                pass
            elif isinstance(p, np.ndarray) & p.shape == (3,):
                pass
            else:
                return False
        return True


class Vec(pg.Vec, Shape):
    pass


class Lin(pg.Lin, Shape):
    pass


class Pln(pg.Pln, Shape):
    pass


class Tgl(pg.Tgl, Shape):

    def intersect(self, ray):
        """"""
        pass

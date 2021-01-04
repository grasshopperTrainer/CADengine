import gkernel.dtype.geometric.primitive as pg
from .shape import Shape


class Ray(pg.Ray, Shape):
    pass


class Pnt(pg.Pnt, Shape):
    pass


class Vec(pg.Vec, Shape):
    pass


class Lin(pg.Lin, Shape):
    pass


class Pln(pg.Pln, Shape):
    pass


class Tgl(pg.Tgl, Shape):
    pass

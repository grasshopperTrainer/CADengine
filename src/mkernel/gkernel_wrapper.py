import gkernel.dtype.geometric.primitive as pg
import mkernel.shape as shp
import mkernel.buffer_syncer as bs
import mkernel.gpu_prgrm as gp
import os


class Ray(pg.Ray, shp.Shape):

    __renderer = shp.ShapeRenderer(bs.BufferSyncer(), gp.GPUPrgrm)

    @classmethod
    def get_cls_renderer(cls):
        return None


class Pnt(pg.Pnt, shp.Shape):
    pass


class Vec(pg.Vec, shp.Shape):
    pass


class Lin(pg.Lin, shp.Shape):
    pass


class Pln(pg.Pln, shp.Shape):
    pass


class Tgl(pg.Tgl, shp.Shape):
    __vrtx_shdr_path = os.path.join(os.path.dirname(__file__), 'tgl_vrtx_shdr.glsl')
    __frgm_shdr_path = os.path.join(os.path.dirname(__file__), 'tgl_frgm_shdr.glsl')

    __prgrm = gp.GPUPrgrm(vrtx=__vrtx_shdr_path, frgm=__frgm_shdr_path)
    __renderer = shp.ShapeRenderer(bs.BufferSyncer(), __prgrm)

    @classmethod
    def get_cls_renderer(cls):
        return cls.__renderer

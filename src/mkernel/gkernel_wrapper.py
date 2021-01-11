import gkernel.dtype.geometric.primitive as pg
import mkernel.shape as shp
import mkernel.buffer_syncer as bs
import ckernel.render_context.opengl_context.entity_template as ogl
import os


class Ray(pg.Ray, shp.Shape):

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
    # path of shaders reletive to current dir
    __vrtx_shdr_path = os.path.join(os.path.dirname(__file__), 'tgl_vrtx_shdr.glsl')
    __frgm_shdr_path = os.path.join(os.path.dirname(__file__), 'tgl_frgm_shdr.glsl')

    # program... but program is per meta context, so this has to happen per context
    __prgrm = ogl.OGLPrgrmTemp(vrtx_path=__vrtx_shdr_path, frgm_path=__frgm_shdr_path)
    __renderer = shp.ShapeRenderer(bs.BufferSyncer(), __prgrm)

    @classmethod
    def get_cls_renderer(cls):
        return cls.__renderer

import os

import ckernel.render_context.opengl_context.meta_entities as meta
from ckernel.render_context.opengl_context.context_stack import get_current_ogl
from ckernel.render_context.opengl_context.meta_entities.prgrm.schemas import VrtxAttrSchema
from ckernel.render_context.opengl_context.meta_entities import *
from ckernel.constants import RENDER_DEFAULT_FLOAT as RDF

from global_tools.singleton import Singleton

"""
Three renderers of dimensional primitives.

A primitive renderer does not only render of its kind.
High dimensional entity is a combination of lower dimensional primitives.
So, a triangle can be viewed in lines and points.
This is why three renderers are atomic.

Shape holdes buffer, buffer cache and vertex array(vao)
, while,
renderer holds prgrm and global uniform cache

"""


THIS_PATH = os.path.dirname(__file__)
def _get_fullpath(rel_path):
    return os.path.join(THIS_PATH, rel_path)


class _PrimitiveRenderer(metaclass=abc.ABCMeta):
    pass


class PointRenderer(_PrimitiveRenderer):
    """
    this is not an expandable, simple functionality wrapper

    prgrm parameter layout:

    ! follow fixed attribute location
    layout (location = 0) in vec4 vtx;
    layout (location = 1) in vec4 clr;
    layout (location = 2) in float dia;
    ... add more to expand render possibility
    :return:

    :param self.__~_prgrm: program rendering sized square points
    :param self.__~_indx_bffr: index buffer storing drawing index of its type
    :param self.__~_ufrm_cache: buffer cache of transformation matrices

    """
    __square_prgrm = fac.PrgrmFactory(
        vrtx_path=os.path.join(os.path.dirname(__file__), 'shaders/pntSqr_vrtx_shdr.glsl'),
        geom_path=os.path.join(os.path.dirname(__file__), 'shaders/pntSqr_geom_shdr.glsl'),
        frgm_path=os.path.join(os.path.dirname(__file__), 'shaders/pntSqr_frgm_shdr.glsl'))

    __circle_prgrm = fac.PrgrmFactory(
        vrtx_path=os.path.join(os.path.dirname(__file__), 'shaders/pntCir_vrtx_shdr.glsl'),
        frgm_path=os.path.join(os.path.dirname(__file__), 'shaders/pntCir_frgm_shdr.glsl'))

    __triangle_prgrm = fac.PrgrmFactory(
        vrtx_path=os.path.join(os.path.dirname(__file__), 'shaders/pntTgl_vrtx_shdr.glsl'),
        geom_path=os.path.join(os.path.dirname(__file__), 'shaders/pntTgl_geom_shdr.glsl'),
        frgm_path=os.path.join(os.path.dirname(__file__), 'shaders/pntTgl_frgm_shdr.glsl'))

    # shared vertex buffer
    __vbo = MetaVrtxBffr(
        attr_desc=np.dtype([('vtx', RDF, 4), ('clr', RDF, 4), ('dia', RDF)]),
        attr_locs=(0, 1, 2))

    def __init__(self):

        self.__square_ufrm_cache = self.__square_prgrm.ufrm_schema.create_bffr_cache(size=1)
        self.__circle_ufrm_cache = self.__circle_prgrm.ufrm_schema.create_bffr_cache(size=1)
        self.__triangle_ufrm_cache = self.__triangle_prgrm.ufrm_schema.create_bffr_cache(size=1)

        self.__circle_ibo = MetaIndxBffr('uint')
        self.__circle_vao = MetaVrtxArry(self.__vbo, indx_bffr=self.__circle_ibo)
        self.__square_ibo = MetaIndxBffr('uint')
        self.__square_vao = MetaVrtxArry(self.__vbo, indx_bffr=self.__square_ibo)
        self.__triangle_ibo = MetaIndxBffr('uint')
        self.__triangle_vao = MetaVrtxArry(self.__vbo, indx_bffr=self.__triangle_ibo)

    @property
    def vbo(self):
        return self.__vbo

    @property
    def circle_ibo(self):
        return self.__circle_ibo

    @property
    def square_ibo(self):
        return self.__square_ibo

    @property
    def triangle_ibo(self):
        return self.__triangle_ibo

    def render(self):
        self.vbo.push_cache()
        self.__render_square()
        self.__render_circle()
        self.__render_triangle()

    def __render_square(self):
        if not self.__square_ibo.cache.active_size:
            return
        with self.__square_vao:
            with self.__square_prgrm as prgrm:
                # update uniforms
                camera = get_current_ogl().manager.window.devices.cameras.current
                self.__square_ufrm_cache['PM'] = camera.body.PM.r
                self.__square_ufrm_cache['VM'] = camera.tripod.VM.r
                self.__square_ufrm_cache['MM'] = [[1, 0, 0, 0],
                                                  [0, 1, 0, 0],
                                                  [0, 0, 1, 0],
                                                  [0, 0, 0, 1]]
                prgrm.push_ufrms(self.__square_ufrm_cache)
                self.__square_ibo.push_cache()
                # mode, count, type, indices
                gl.glDrawElements(gl.GL_POINTS,
                                  self.__square_ibo.cache.active_size,
                                  self.__square_ibo.cache.gldtype[0],
                                  ctypes.c_void_p(0))

    def __render_circle(self):
        if not self.__circle_ibo.cache.active_size:
            return
        with self.__circle_vao:
            with self.__circle_prgrm as prgrm:
                # update uniforms
                camera = get_current_ogl().manager.window.devices.cameras.current

                self.__circle_ufrm_cache['PM'] = camera.body.PM.r
                self.__circle_ufrm_cache['VM'] = camera.tripod.VM.r
                self.__circle_ufrm_cache['MM'] = [[1, 0, 0, 0],
                                                  [0, 1, 0, 0],
                                                  [0, 0, 1, 0],
                                                  [0, 0, 0, 1]]
                self.__circle_ufrm_cache['VS'] = get_current_ogl().manager.window.devices.panes.current.size
                prgrm.push_ufrms(self.__circle_ufrm_cache)
                self.__circle_ibo.push_cache()
                gl.glDrawElements(gl.GL_POINTS,
                                  self.__circle_ibo.cache.active_size,
                                  self.__circle_ibo.cache.gldtype[0],
                                  ctypes.c_void_p(0))

    def __render_triangle(self):
        if not self.__triangle_ibo.cache.active_size:
            return
        with self.__triangle_vao:
            with self.__triangle_prgrm as prgrm:
                # update uniforms
                camera = get_current_ogl().manager.window.devices.cameras.current

                self.__triangle_ufrm_cache['PM'] = camera.body.PM.r
                self.__triangle_ufrm_cache['VM'] = camera.tripod.VM.r
                self.__triangle_ufrm_cache['MM'] = [[1, 0, 0, 0],
                                                    [0, 1, 0, 0],
                                                    [0, 0, 1, 0],
                                                    [0, 0, 0, 1]]
                prgrm.push_ufrms(self.__triangle_ufrm_cache)
                self.__triangle_ibo.push_cache()
                gl.glDrawElements(gl.GL_POINTS,
                                  self.__triangle_ibo.cache.active_size,
                                  self.__triangle_ibo.cache.gldtype[0],
                                  ctypes.c_void_p(0))


class LineRenderer(_PrimitiveRenderer):
    """
    prgrm parameter layout:

    ! programs should follow fixed attribute locations
    layout (location = 0) in vec4 vtx;
    layout (location = 1) in float thk;
    layout (location = 2) in vec4 clr;
    ... add more to expand render possibility

    :param self.__sharp_prgrm: program rendering thick sharp line
    :param self.__trnsf_ufrm_cache: buffer cache of transformation matrices
    """
    __sharp_prgrm = fac.PrgrmFactory(
        vrtx_path=os.path.join(os.path.dirname(__file__), 'shaders/linSharp_vrtx_shdr.glsl'),
        geom_path=os.path.join(os.path.dirname(__file__), 'shaders/linSharp_geom_shdr.glsl'),
        frgm_path=os.path.join(os.path.dirname(__file__), 'shaders/linSharp_frgm_shdr.glsl'))

    __vbo = MetaVrtxBffr(
        attr_desc=np.dtype([('vtx', RDF, 4), ('thk', RDF), ('clr', RDF, 4)]),
        attr_locs=(0, 1, 2))

    def __init__(self):
        self.__ufrm_cache = self.__sharp_prgrm.ufrm_schema.create_bffr_cache(size=1)
        self.__ibo = MetaIndxBffr(dtype='uint')
        self.__vao = MetaVrtxArry(self.__vbo, indx_bffr=self.__ibo)

    @property
    def vbo(self):
        return self.__vbo

    @property
    def ibo(self):
        return self.__ibo

    def render(self):
        self.__vbo.push_cache()
        self.__render_sharp()

    def __render_sharp(self):
        if not self.__ibo.cache.active_size:
            return
        with self.__vao:
            with self.__sharp_prgrm as prgrm:
                camera = get_current_ogl().manager.window.devices.cameras.current
                self.__ufrm_cache['VM'] = camera.tripod.VM.r
                self.__ufrm_cache['PM'] = camera.body.PM.r
                self.__ufrm_cache['MM'] = [[1, 0, 0, 0],
                                           [0, 1, 0, 0],
                                           [0, 0, 1, 0],
                                           [0, 0, 0, 1]]
                prgrm.push_ufrms(self.__ufrm_cache)
                self.__ibo.push_cache()
                gl.glDrawElements(gl.GL_LINES,
                                  self.__ibo.cache.active_size,
                                  self.__ibo.cache.gldtype[0],
                                  ctypes.c_void_p(0))

@Singleton
class PolylineRenderer(_PrimitiveRenderer):
    def __init__(self):
        self.__sharp_prgrm = meta.MetaPrgrm(
            vrtx_path=_get_fullpath('shaders/plinSharp_vrtx_shdr.glsl'),
            geom_path=_get_fullpath('shaders/plinSharp_geom_shdr.glsl'),
            frgm_path=_get_fullpath('shaders/plinSharp_frgm_shdr.glsl')
        )
        self.__vbo = MetaVrtxBffr(
            attr_desc=np.dtype([('vtx', 'f4', 4), ('thk', 'f4'), ('clr', 'f4', 4)]),
            attr_locs=(0, 1, 2)
        )
        self.__ibo = MetaIndxBffr(dtype='uint')
        self.__vao = MetaVrtxArry(self.__vbo, indx_bffr=self.__ibo)

        self.__ufrm_cache = self.__sharp_prgrm.ufrm_schema.create_bffr_cache(size=1)

    @property
    def vbo(self):
        return self.__vbo

    @property
    def ibo(self):
        return self.__ibo

    def render(self):
        self.__vbo.push_cache()
        self.__ibo.push_cache()
        self.__render_sharp()

    def __render_sharp(self):
        if not self.__ibo.cache.active_size:
            return
        with self.__vao:
            with self.__sharp_prgrm as prgrm:
                # uniforms
                camera = get_current_ogl().manager.window.devices.cameras.current
                self.__ufrm_cache['VM'] = camera.tripod.VM.r
                self.__ufrm_cache['PM'] = camera.body.PM.r
                self.__ufrm_cache['MM'] = [[1, 0, 0, 0],
                                           [0, 1, 0, 0],
                                           [0, 0, 1, 0],
                                           [0, 0, 0, 1]]
                prgrm.push_ufrms(self.__ufrm_cache)

                gl.glDrawElements(gl.GL_LINE_STRIP,
                                  self.__ibo.cache.active_size,
                                  self.__ibo.cache.gldtype[0],
                                  ctypes.c_void_p(0))

class TriangleRenderer(_PrimitiveRenderer):
    """
    full spec schema of triangle object.

    use this schema as programs are not obliged to implement all attributes

    ! programs should follow fixed attribute name and locations
    layout(location = 0) in vtx;
    layout(location = 1) in edge_thk;
    layout(location = 2) in edge_clr;
    layout(location = 3) in fill_clr;
    ... add more to expand render possibility

    :param self.__fill_prgrm: for rendering triangle fill
    :param self.__edge_prgrm: for rendering triangle thick edge
    :param self.__trnsf_ufrm_cache: buffer cache of transformation matrices
    """
    __fill_prgrm = fac.PrgrmFactory(
        vrtx_path=os.path.join(os.path.dirname(__file__), 'shaders/tglFill_vrtx_shdr.glsl'),
        frgm_path=os.path.join(os.path.dirname(__file__), 'shaders/tglFill_frgm_shdr.glsl'))

    __edge_prgrm = fac.PrgrmFactory(
        vrtx_path=os.path.join(os.path.dirname(__file__), 'shaders/tglSharpEdge_vrtx_shdr.glsl'),
        geom_path=os.path.join(os.path.dirname(__file__), 'shaders/tglSharpEdge_geom_shdr.glsl'),
        frgm_path=os.path.join(os.path.dirname(__file__), 'shaders/tglSharpEdge_frgm_shdr.glsl'))

    __vbo = MetaVrtxBffr(
        attr_desc=np.dtype([('vtx', RDF, 4), ('edge_thk', RDF), ('edge_clr', RDF, 4), ('fill_clr', RDF, 4)]),
        attr_locs=(0, 1, 2, 3))

    def __init__(self):
        self.__ufrm_cache = self.__fill_prgrm.ufrm_schema.create_bffr_cache(size=1)
        self.__ibo = MetaIndxBffr('uint')
        self.__vao = MetaVrtxArry(self.__vbo, indx_bffr=self.__ibo)

    @property
    def vbo(self):
        return self.__vbo

    @property
    def ibo(self):
        return self.__ibo

    def __update_global_ufrm(self, prgrm):
        """
        update transformation uniforms
        :return:
        """
        camera = get_current_ogl().manager.window.devices.cameras.current
        vm = camera.tripod.VM.r
        pm = camera.body.PM.r
        self.__ufrm_cache['VM'] = vm
        self.__ufrm_cache['PM'] = pm
        self.__ufrm_cache['MM'] = [[1, 0, 0, 0],
                                   [0, 1, 0, 0],
                                   [0, 0, 1, 0],
                                   [0, 0, 0, 1]]
        prgrm.push_ufrms(self.__ufrm_cache)

    def render(self, is_render_edge=True):
        """

        :param is_render_edge: bool, do render edge?
        :return:
        """
        self.__vbo.get_concrete().push_cache()
        self.__ibo.get_concrete().push_cache()
        with self.__vao:
            self.__render_fill()
            if is_render_edge:
                self.__render_edge()

    def __render_fill(self):
        if not self.__ibo.cache.active_size:
            return
        with self.__fill_prgrm as prgrm:
            self.__update_global_ufrm(prgrm)
            gl.glDrawElements(gl.GL_TRIANGLES,
                              self.__ibo.cache.active_size,
                              self.__ibo.cache.gldtype[0],
                              ctypes.c_void_p(0))

    def __render_edge(self):
        if not self.__ibo.cache.active_size:
            return
        with self.__edge_prgrm as prgrm:
            self.__update_global_ufrm(prgrm)
            gl.glDrawElements(gl.GL_TRIANGLES,
                              self.__ibo.cache.active_size,
                              self.__ibo.cache.gldtype[0],
                              ctypes.c_void_p(0))

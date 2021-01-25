import os

import ckernel.render_context.opengl_context.factories as fac
from ckernel.render_context.opengl_context.context_stack import get_current_ogl
from ckernel.render_context.opengl_context.factories.prgrm.schemas import VrtxAttrSchema
from ckernel.render_context.opengl_context.factories import *
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


class _PrimitiveRenderer(metaclass=abc.ABCMeta):
    pass


# better use singleton for flexibility like adding @property; better protection
@Singleton
class PointRenderer(_PrimitiveRenderer):
    """
    this is not an expandable, simple functionality wrapper
    """

    def __init__(self):
        """
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

        self.__square_prgrm = fac.PrgrmFactory(
            vrtx_path=os.path.join(os.path.dirname(__file__), 'shaders/pntSqr_vrtx_shdr.glsl'),
            geom_path=os.path.join(os.path.dirname(__file__), 'shaders/pntSqr_geom_shdr.glsl'),
            frgm_path=os.path.join(os.path.dirname(__file__), 'shaders/pntSqr_frgm_shdr.glsl'))
        self.__square_ufrm = self.__square_prgrm.ufrm_schema.create_bffr_cache(size=1)

        self.__circle_prgrm = fac.PrgrmFactory(
            vrtx_path=os.path.join(os.path.dirname(__file__), 'shaders/pntCir_vrtx_shdr.glsl'),
            frgm_path=os.path.join(os.path.dirname(__file__), 'shaders/pntCir_frgm_shdr.glsl'))
        self.__circle_ufrm_cache = self.__circle_prgrm.ufrm_schema.create_bffr_cache(size=1)

        self.__triangle_prgrm = fac.PrgrmFactory(
            vrtx_path=os.path.join(os.path.dirname(__file__), 'shaders/pntTgl_vrtx_shdr.glsl'),
            geom_path=os.path.join(os.path.dirname(__file__), 'shaders/pntTgl_geom_shdr.glsl'),
            frgm_path=os.path.join(os.path.dirname(__file__), 'shaders/pntTgl_frgm_shdr.glsl'))
        self.__triangle_ufrm_cache = self.__triangle_prgrm.ufrm_schema.create_bffr_cache(size=1)

        # shared vertex buffer
        schema = VrtxAttrSchema(dtype=np.dtype([('vtx', RDF, 4), ('clr', RDF, 4), ('dia', RDF)]), locs=(0, 1, 2))
        self.__vbo = VrtxBffrFactory(schema.dtype, schema.locs)

        self.__circle_ibo = IndxBffrFactory('uint')
        self.__circle_vao = VrtxArryFactory(self.__vbo, indx_bffr=self.__circle_ibo)
        self.__square_ibo = IndxBffrFactory('uint')
        self.__square_vao = VrtxArryFactory(self.__vbo, indx_bffr=self.__square_ibo)
        self.__triangle_ibo = IndxBffrFactory('uint')
        self.__triangle_vao = VrtxArryFactory(self.__vbo, indx_bffr=self.__triangle_ibo)

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
        PointRenderer().vbo.get_entity().push_cache()
        self.__render_square()
        self.__render_circle()
        self.__render_triangle()

    def __render_square(self):
        with self.__square_vao:
            with self.__square_prgrm as prgrm:
                # update uniforms
                camera = get_current_ogl().manager.window.devices.cameras.current
                self.__square_ufrm['PM'] = camera.body.PM.r
                self.__square_ufrm['VM'] = camera.tripod.VM.r
                self.__square_ufrm['MM'] = [[1, 0, 0, 0],
                                            [0, 1, 0, 0],
                                            [0, 0, 1, 0],
                                            [0, 0, 0, 1]]
                prgrm.push_ufrms(self.__square_ufrm)
                self.__square_ibo.get_entity().push_cache()
                # mode, count, type, indices
                gl.glDrawElements(gl.GL_POINTS,
                                  len(self.__circle_ibo.cache),
                                  self.__circle_ibo.cache.gldtype[0],
                                  ctypes.c_void_p(0))

    def __render_circle(self):
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
                self.__circle_ibo.get_entity().push_cache()
                gl.glDrawElements(gl.GL_POINTS,
                                  len(self.__circle_ibo.cache),
                                  self.__circle_ibo.cache.gldtype[0],
                                  ctypes.c_void_p(0))

    def __render_triangle(self):
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
                self.__triangle_ibo.get_entity().push_cache()
                gl.glDrawElements(gl.GL_POINTS,
                                  len(self.__triangle_ibo.cache),
                                  self.__triangle_ibo.cache.gldtype[0],
                                  ctypes.c_void_p(0))

@Singleton
class LineRenderer(_PrimitiveRenderer):

    def __init__(self):
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
        self.__sharp_prgrm = fac.PrgrmFactory(
            vrtx_path=os.path.join(os.path.dirname(__file__), 'shaders/linSharp_vrtx_shdr.glsl'),
            geom_path=os.path.join(os.path.dirname(__file__), 'shaders/linSharp_geom_shdr.glsl'),
            frgm_path=os.path.join(os.path.dirname(__file__), 'shaders/linSharp_frgm_shdr.glsl'))

        self.__global_ufrm_cache = self.__sharp_prgrm.ufrm_schema.create_bffr_cache(size=1)

        self.__vbo = VrtxBffrFactory(
            attr_desc=np.dtype([('vtx', RDF, 4), ('thk', RDF), ('clr', RDF, 4)]),
            attr_locs=(0, 1, 2))
        self.__ibo = IndxBffrFactory(dtype='uint')
        self.__vao = VrtxArryFactory(self.__vbo, indx_bffr=self.__ibo)

    @property
    def vbo(self):
        return self.__vbo

    @property
    def ibo(self):
        return self.__ibo

    def render(self):
        self.__vbo.get_entity().push_cache()
        self.__render_sharp()

    def __render_sharp(self):
        vao = self.__vao.get_entity()
        prgrm = self.__sharp_prgrm.get_entity()
        with vao:
            with prgrm:
                camera = get_current_ogl().manager.window.devices.cameras.current
                vm = camera.tripod.VM.r
                pm = camera.body.PM.r
                self.__global_ufrm_cache['VM'] = vm
                self.__global_ufrm_cache['PM'] = pm
                self.__global_ufrm_cache['MM'] = [[1, 0, 0, 0],
                                                  [0, 1, 0, 0],
                                                  [0, 0, 1, 0],
                                                  [0, 0, 0, 1]]
                prgrm.push_ufrms(self.__global_ufrm_cache)
                self.__ibo.get_entity().push_cache()
                gl.glDrawElements(gl.GL_LINES,
                                  len(self.__ibo.cache),
                                  self.__ibo.cache.gldtype[0],
                                  ctypes.c_void_p(0))


@Singleton
class TriangleRenderer(_PrimitiveRenderer):

    def __init__(self):
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
        self.__fill_prgrm = fac.PrgrmFactory(
            vrtx_path=os.path.join(os.path.dirname(__file__), 'shaders/tglFill_vrtx_shdr.glsl'),
            frgm_path=os.path.join(os.path.dirname(__file__), 'shaders/tglFill_frgm_shdr.glsl'))

        self.__edge_prgrm = fac.PrgrmFactory(
            vrtx_path=os.path.join(os.path.dirname(__file__), 'shaders/tglSharpEdge_vrtx_shdr.glsl'),
            geom_path=os.path.join(os.path.dirname(__file__), 'shaders/tglSharpEdge_geom_shdr.glsl'),
            frgm_path=os.path.join(os.path.dirname(__file__), 'shaders/tglSharpEdge_frgm_shdr.glsl'))
        self.__ufrm_cache = self.__fill_prgrm.ufrm_schema.create_bffr_cache(size=1)

        self.__vbo = VrtxBffrFactory(
            attr_desc=np.dtype([('vtx', RDF, 4), ('edge_thk', RDF), ('edge_clr', RDF, 4), ('fill_clr', RDF, 4)]),
            attr_locs=(0, 1, 2, 3))
        self.__ibo = IndxBffrFactory('uint')
        self.__vao = VrtxArryFactory(self.__vbo, indx_bffr=self.__ibo)

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

    def render(self, is_render_edge):
        """

        :param is_render_edge: bool, do render edge?
        :return:
        """
        self.__vbo.get_entity().push_cache()
        self.__ibo.get_entity().push_cache()
        with self.__vao:
            self.__render_fill()
            if is_render_edge:
                self.__render_edge()

    def __render_fill(self):
        with self.__fill_prgrm as prgrm:
            self.__update_global_ufrm(prgrm)
            gl.glDrawElements(gl.GL_TRIANGLES,
                              len(self.__ibo.cache),
                              self.__ibo.cache.gldtype[0],
                              ctypes.c_void_p(0))

    def __render_edge(self):
        with self.__edge_prgrm as prgrm:
            self.__update_global_ufrm(prgrm)
            gl.glDrawElements(gl.GL_TRIANGLES,
                              len(self.__ibo.cache),
                              self.__ibo.cache.gldtype[0],
                              ctypes.c_void_p(0))

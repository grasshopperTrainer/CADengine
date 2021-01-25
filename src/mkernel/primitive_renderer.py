import os
import abc
import numpy as np
import ctypes

import ckernel.render_context.opengl_context.opengl_hooker as gl
import ckernel.render_context.opengl_context.factories as fac
from ckernel.render_context.opengl_context.context_stack import get_current_ogl
from ckernel.render_context.opengl_context.factories.prgrm.schemas import VrtxAttrSchema
from ckernel.render_context.opengl_context.factories import *
from ckernel.constants import DEF_RENDER_FLOAT_STR as RF

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

    @property
    @abc.abstractmethod
    def vrtx_attr_schema(self):
        """
        :return: full spec vertex attribute schema
        """
        pass


# better use singleton for flexibility like adding @property; better protection
@Singleton
class PointRenderer(_PrimitiveRenderer):
    """
    this is not an expandable, simple functionality wrapper
    """

    def __init__(self):
        """
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
        self.__circle_ufrm = self.__circle_prgrm.ufrm_schema.create_bffr_cache(size=1)

        # shared vertex buffer
        schema = VrtxAttrSchema(dtype=np.dtype([('vtx', RF, 4), ('clr', RF, 4), ('dia', RF, 1)]), locs=(0, 1, 2))
        self.__vrtx_bffr = VrtxBffrFactory(schema.dtype, schema.locs)

        self.__circle_ibo = IndxBffrFactory('uint')
        self.__circle_vao = VrtxArryFactory(self.__vrtx_bffr, indx_bffr=self.__circle_ibo)
        self.__square_ibo = IndxBffrFactory('uint')
        self.__square_vao = VrtxArryFactory(self.__vrtx_bffr, indx_bffr=self.__square_ibo)

    @property
    def vrtx_attr_schema(self):
        """
        prgrm parameter layout:

        ! follow fixed attribute location
        layout (location = 0) in vec4 vtx;
        layout (location = 1) in vec4 clr;
        layout (location = 2) in float dia;
        ... add more to expand render possibility
        :return:
        """
        return VrtxAttrSchema(
            dtype=np.dtype([('vtx', RF, 4), ('clr', RF, 4), ('dia', RF, 1)]),
            locs=(0, 1, 2))

    @property
    def vrtx_bffr(self):
        return self.__vrtx_bffr

    @property
    def circls_indx_bffr(self):
        return self.__circle_ibo

    @property
    def square_indx_bffr(self):
        return self.__square_ibo

    def render_square(self):
        vao = self.__square_vao.get_entity()
        prgrm = self.__square_prgrm.get_entity()
        with vao:
            with prgrm:
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

    def render_circle(self):
        vao = self.__circle_vao.get_entity()
        prgrm = self.__circle_prgrm.get_entity()
        with vao:
            with prgrm:
                # update uniforms
                camera = get_current_ogl().manager.window.devices.cameras.current

                self.__circle_ufrm['PM'] = camera.body.PM.r
                self.__circle_ufrm['VM'] = camera.tripod.VM.r
                self.__circle_ufrm['MM'] = [[1, 0, 0, 0],
                                            [0, 1, 0, 0],
                                            [0, 0, 1, 0],
                                            [0, 0, 0, 1]]
                self.__circle_ufrm['VS'] = get_current_ogl().manager.window.devices.panes.current.size
                prgrm.push_ufrms(self.__circle_ufrm)
                self.__circle_ibo.get_entity().push_cache()
                gl.glDrawElements(gl.GL_POINTS,
                                  len(self.__circle_ibo.cache),
                                  self.__circle_ibo.cache.gldtype[0],
                                  ctypes.c_void_p(0))


@Singleton
class LineRenderer(_PrimitiveRenderer):

    def __init__(self):
        """
        :param self.__sharp_prgrm: program rendering thick sharp line
        :param self.__trnsf_ufrm_cache: buffer cache of transformation matrices
        """
        self.__sharp_prgrm = fac.PrgrmFactory(
            vrtx_path=os.path.join(os.path.dirname(__file__), 'shaders/linSharp_vrtx_shdr.glsl'),
            geom_path=os.path.join(os.path.dirname(__file__), 'shaders/linSharp_geom_shdr.glsl'),
            frgm_path=os.path.join(os.path.dirname(__file__), 'shaders/linSharp_frgm_shdr.glsl'))

        self.__global_ufrm_cache = self.__sharp_prgrm.ufrm_schema.create_bffr_cache(size=1)

    @property
    def vrtx_attr_schema(self):
        """
        prgrm parameter layout:

        ! programs should follow fixed attribute locations
        layout (location = 0) in vec4 vtx;
        layout (location = 1) in float thk;
        layout (location = 2) in vec4 clr;
        ... add more to expand render possibility
        """
        return VrtxAttrSchema(
            dtype=np.dtype([('vtx', RF, 4), ('thk', RF, (1,)), ('clr', RF, 4)]),
            locs=(0, 1, 2))

    def __update_global_ufrm(self, prgrm):
        """
        update transformation uniforms
        :return:
        """
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

    def render_sharp(self, vrtx_count):
        prgrm = self.__sharp_prgrm.get_entity()
        with prgrm:
            self.__update_global_ufrm(prgrm)
            gl.glDrawArrays(gl.GL_LINES, 0, vrtx_count)


@Singleton
class TriangleRenderer(_PrimitiveRenderer):

    def __init__(self):
        """
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
        self.__global_ufrm_cache = self.__fill_prgrm.ufrm_schema.create_bffr_cache(size=1)

    @property
    def vrtx_attr_schema(self):
        """
        full spec schema of triangle object.

        use this schema as programs are not obliged to implement all attributes

        ! programs should follow fixed attribute name and locations
        layout(location = 0) in vtx;
        layout(location = 1) in edge_thk;
        layout(location = 2) in edge_clr;
        layout(location = 3) in fill_clr;
        ... add more to expand render possibility
        :return:
        """
        return VrtxAttrSchema(
            dtype=np.dtype([('vtx', RF, 4), ('edge_thk', RF, (1,)), ('edge_clr', RF, 4), ('fill_clr', RF, 4)]),
            locs=(0, 1, 2, 3))

    def __update_global_ufrm(self, prgrm):
        """
        update transformation uniforms
        :return:
        """
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

    def render_fill(self, vrtx_count):
        prgrm = self.__fill_prgrm.get_entity()
        with prgrm:
            self.__update_global_ufrm(prgrm)
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, vrtx_count)

    def render_edge(self, vrtx_count):
        prgrm = self.__edge_prgrm.get_entity()
        with prgrm:
            self.__update_global_ufrm(prgrm)
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, vrtx_count)

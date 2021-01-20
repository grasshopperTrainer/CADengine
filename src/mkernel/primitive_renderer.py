import os
import abc

import ckernel.render_context.opengl_context.opengl_hooker as gl
import ckernel.render_context.opengl_context.factories as fac
from ckernel.render_context.opengl_context.context_stack import get_current_ogl
from ckernel.render_context.opengl_context.uniform_pusher import UniformPusher
from ckernel.render_context.opengl_context.bffr_cache import BffrCache


"""
Three renderers of dimensional primitives.

A primitive renderer does not only render of its kind.
High dimensional entity is a combination of lower dimensional primitives.
So, a triangle can be viewed in lines and points.
This is why three renderers are atomic.

Shape holdes buffer, buffer cache and vertex array(vao)
, while,
renderer holds prgrm and global uniform cache

prgrm structure:
! follow fixed attribute location
layout(location = 0) in vtx;
layout(location = 1) in edge_thk;
layout(location = 2) in edge_clr;
layout(location = 3) in clr_fill;

"""


class _PrimitiveRenderer(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def render(self, vao):
        """
        render call, OpenGL render functions are called inside this scope

        labor division:
        1. render call does nothing with buffer updating.
        It has to be dealt prior calling this method.
        2. vao is bound inside the method.
        Program cant render with its own. Vertex Array has to be present
        :return:
        """


class PointRenderer:
    pass


class LineRenderer:
    __vrtx_shdr_path = os.path.join(os.path.dirname(__file__), 'shaders/lin_vrtx_shdr.glsl')
    __frgm_shdr_path = os.path.join(os.path.dirname(__file__), 'shaders/lin_frgm_shdr.glsl')
    __prgrm = fac.PrgrmFactory(vrtx_path=__vrtx_shdr_path, frgm_path=__frgm_shdr_path)

    __ufrm_cache = __prgrm.ufrm_skema.create_bffr_cache(size=1)

    @classmethod
    def render(cls, vao, vrtx_count):
        with vao:
            with cls.__prgrm:
                camera = get_current_ogl().manager.window.devices.cameras.current
                vm = camera.tripod.VM.r
                pm = camera.body.PM.r
                cls.__ufrm_cache['VM'] = vm
                cls.__ufrm_cache['PM'] = pm
                cls.__ufrm_cache['MM'] = [[1, 0, 0, 0],
                                          [0, 1, 0, 0],
                                          [0, 0, 1, 0],
                                          [0, 0, 0, 1]]

                # update uniform data
                UniformPusher.push_all(cls.__ufrm_cache, cls.__prgrm)

                gl.glDrawArrays(gl.GL_LINE_LOOP,
                                0,
                                vrtx_count)


class TriangleRenderer(_PrimitiveRenderer):
    __vrtx_shdr_path = os.path.join(os.path.dirname(__file__), 'shaders/tglFill_vrtx_shdr.glsl')
    __frgm_shdr_path = os.path.join(os.path.dirname(__file__), 'shaders/tglFill_frgm_shdr.glsl')
    __prgrm = fac.PrgrmFactory(vrtx_path=__vrtx_shdr_path, frgm_path=__frgm_shdr_path)

    __ufrm_cache = __prgrm.ufrm_skema.create_bffr_cache(size=1)

    @classmethod
    def render(cls, vao, vrtx_count):
        with vao:
            with cls.__prgrm:
                camera = get_current_ogl().manager.window.devices.cameras.current
                vm = camera.tripod.VM.r
                pm = camera.body.PM.r
                cls.__ufrm_cache['VM'] = vm
                cls.__ufrm_cache['PM'] = pm
                cls.__ufrm_cache['MM'] = [[1, 0, 0, 0],
                                          [0, 1, 0, 0],
                                          [0, 0, 1, 0],
                                          [0, 0, 0, 1]]

                # update uniform data
                UniformPusher.push_all(cls.__ufrm_cache, cls.__prgrm)

                gl.glDrawArrays(gl.GL_TRIANGLES,
                                0,
                                vrtx_count)


class TriangleEdgeRenderer(_PrimitiveRenderer):
    __vrtx_shdr_path = os.path.join(os.path.dirname(__file__), 'shaders/tglSharpEdge_vrtx_shdr.glsl')
    __geom_shdr_path = os.path.join(os.path.dirname(__file__), 'shaders/tglSharpEdge_geom_shdr.glsl')
    __frgm_shdr_path = os.path.join(os.path.dirname(__file__), 'shaders/tglSharpEdge_frgm_shdr.glsl')
    __prgrm = fac.PrgrmFactory(vrtx_path=__vrtx_shdr_path, geom_path=__geom_shdr_path, frgm_path=__frgm_shdr_path)

    __ufrm_cache = __prgrm.ufrm_skema.create_bffr_cache(size=1)

    @classmethod
    def render(cls, vao, vrtx_count):
        with vao:
            with cls.__prgrm:
                camera = get_current_ogl().manager.window.devices.cameras.current
                vm = camera.tripod.VM.r
                pm = camera.body.PM.r
                cls.__ufrm_cache['VM'] = vm
                cls.__ufrm_cache['PM'] = pm
                cls.__ufrm_cache['MM'] = [[1, 0, 0, 0],
                                          [0, 1, 0, 0],
                                          [0, 0, 1, 0],
                                          [0, 0, 0, 1]]

                # update uniform data
                UniformPusher.push_all(cls.__ufrm_cache, cls.__prgrm)

                gl.glDrawArrays(gl.GL_TRIANGLES,
                                0,
                                vrtx_count)
import ctypes as ct

import ckernel.render_context.opengl_context.meta_entities as meta
from .base import _Renderer, get_shader_fullpath
from ckernel.render_context.opengl_context.context_stack import get_current_ogl
import ckernel.render_context.opengl_context.opengl_hooker as gl


class PolygonRenderer(_Renderer):
    """

    """
    __fill_prgrm = meta.MetaPrgrm(
        vrtx_path=get_shader_fullpath('shaders/pgon/pgonFill_vrtx_shdr.glsl'),
        frgm_path=get_shader_fullpath('shaders/pgon/pgonFill_frgm_shdr.glsl'))

    __edge_prgrm = meta.MetaPrgrm(
        vrtx_path=get_shader_fullpath('shaders/pgon/pgonSharpEdge_vrtx_shdr.glsl'),
        geom_path=get_shader_fullpath('shaders/pgon/pgonSharpEdge_geom_shdr.glsl'),
        frgm_path=get_shader_fullpath('shaders/pgon/pgonSharpEdge_frgm_shdr.glsl')
    )

    __vbo = __fill_prgrm.vrtxattr_schema.create_vrtx_bffr_fac()
    __ufrm_cache = __fill_prgrm.ufrm_cache
    __ufrm_block = __ufrm_cache.request_block(size=1)

    def __init__(self):
        self.__fill_ibo = meta.MetaIndxBffr(dtype='uint')
        self.__fill_vao = meta.MetaVrtxArry(self.__vbo, indx_bffr=self.__fill_ibo)
        self.__edge_ibo = meta.MetaIndxBffr(dtype='uint')
        self.__edge_vao = meta.MetaVrtxArry(self.__vbo, indx_bffr=self.__edge_ibo)

    @property
    def vbo(self):
        return self.__vbo

    @property
    def fill_ibo(self):
        return self.__fill_ibo

    @property
    def edge_ibo(self):
        return self.__edge_ibo

    def render(self):
        self.__vbo.push_cache()
        self.__render_fill()
        self.__render_edge()

    def __render_fill(self):
        self.__fill_ibo.push_cache()
        with self.__fill_vao:
            with self.__fill_prgrm:
                # update uniforms
                camera = get_current_ogl().manager.window.devices.cameras.current
                self.__ufrm_block['PM'] = camera.body.PM
                self.__ufrm_block['VM'] = camera.tripod.VM
                self.__ufrm_block['MM'] = [[1, 0, 0, 0],
                                           [0, 1, 0, 0],
                                           [0, 0, 1, 0],
                                           [0, 0, 0, 1]]
                self.__fill_prgrm.push_external_ufrm_cache(self.__ufrm_cache)

                gl.glDrawElements(gl.GL_QUAD_STRIP,
                                  self.__fill_ibo.cache.active_size,
                                  self.__fill_ibo.cache.gldtype[0],
                                  ct.c_void_p(0))

    def __render_edge(self):
        self.__edge_ibo.push_cache()
        # gl.glLineWidth(3)
        with self.__edge_vao:
            with self.__edge_prgrm:
                # update uniforms
                # update uniforms
                camera = get_current_ogl().manager.window.devices.cameras.current
                self.__ufrm_block['PM'] = camera.body.PM
                self.__ufrm_block['VM'] = camera.tripod.VM
                self.__ufrm_block['MM'] = [[1, 0, 0, 0],
                                           [0, 1, 0, 0],
                                           [0, 0, 1, 0],
                                           [0, 0, 0, 1]]
                self.__edge_prgrm.push_external_ufrm_cache(self.__ufrm_cache)

                gl.glDrawElements(gl.GL_LINE_STRIP_ADJACENCY,
                                  self.__edge_ibo.cache.active_size,
                                  self.__edge_ibo.cache.gldtype[0],
                                  ct.c_void_p(0))

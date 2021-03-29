import ctypes
import OpenGL.GL as gl
import numpy as np

from .base import _Renderer, get_shader_fullpath
import ckernel.render_context.opengl_context.meta_entities as meta
from ckernel.render_context.opengl_context.context_stack import get_current_ogl


class PlaneRenderer(_Renderer):
    __prgrm = meta.MetaPrgrm(vrtx_path=get_shader_fullpath('shaders/plane_vrtx_shdr.glsl'),
                             geom_path=get_shader_fullpath('shaders/plane_geom_shdr.glsl'),
                             frgm_path=get_shader_fullpath('shaders/plane_frgm_shdr.glsl'))

    def __init__(self):
        self.__vbo = self.__prgrm.vrtxattr_schema.create_vrtx_bffr()
        self.__ibo = meta.MetaIndxBffr(dtype='uint')
        self.__vao = meta.MetaVrtxArry(self.__vbo, indx_bffr=self.__ibo)

    @property
    def vbo(self):
        return self.__vbo

    @property
    def ibo(self):
        return self.__ibo

    def render(self):
        with self.__prgrm:
            camera = get_current_ogl().manager.window.devices.cameras.current
            self.__prgrm.uniforms['PM'] = camera.body.PM
            self.__prgrm.uniforms['VM'] = camera.tripod.VM
            self.__prgrm.uniforms['MM'] = np.eye(4)
            self.__prgrm.push_uniforms()

            with self.__vao:
                self.__vbo.push_cache()
                self.__ibo.push_cache()

                gl.glDrawElements(gl.GL_POINTS,
                                  self.__ibo.cache.active_size,
                                  self.__ibo.cache.gldtype[0],
                                  ctypes.c_void_p(0))


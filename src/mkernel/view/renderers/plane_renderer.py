import ctypes
import OpenGL.GL as gl
import numpy as np

from .base import Renderer, get_shader_fullpath
import ckernel.render_context.opengl_context.entities.meta as meta
from ckernel.render_context.opengl_context.context_stack import get_current_ogl


class PlaneRenderer(Renderer):
    __prgrm = meta.MetaPrgrm(vrtx_path=get_shader_fullpath('shaders/plane_vrtx_shdr.glsl'),
                             geom_path=get_shader_fullpath('shaders/plane_geom_shdr.glsl'),
                             frgm_path=get_shader_fullpath('shaders/plane_frgm_shdr.glsl'))

    def __init__(self):
        super().__init__()

        self.__vbo = self.__prgrm.vrtx_attr_schema.create_vrtx_bffr()
        self.__ibo = meta.MetaIndxBffr(dtype='uint')
        self.__vao = meta.MetaVrtxArry(self.__vbo, indx_bffr=self.__ibo)

    def create_dataset(self, size):
        vb = self.__vbo.cache.request_block(size)
        ib = self.__ibo.cache.request_block(size)
        ib['idx'] = vb.indices
        return {'vrtx': vb, 'indx': ib}

    def free_finalizer(self, dataset):
        if dataset:
            for block in dataset.values():
                block.release()
            dataset.clear()

    def update_cache(self, shape, arg_name, value):
        self.datasets[shape]['vrtx'][arg_name] = value

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

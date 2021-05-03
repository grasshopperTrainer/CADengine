import os
import OpenGL.GL as gl

import ckernel.render_context.opengl_context.entities.meta as meta
from ckernel.render_context.opengl_context.context_stack import get_current_ogl

from .base import Renderer, get_shader_fullpath


class GroundRenderer(Renderer):
    """
    draw infinite ground
    """
    __prgrm = meta.MetaPrgrm(vrtx_path=get_shader_fullpath('shaders/ground_vrtx_shdr.glsl'),
                             frgm_path=get_shader_fullpath('shaders/ground_frgm_shdr.glsl'))

    def __init__(self):
        super().__init__()

        self.__vbo = self.__prgrm.vrtx_attr_schema.create_vrtx_bffr()
        self.__vao = meta.MetaVrtxArry(self.__vbo)

    def create_dataset(self, size):
        vb = self.__vbo.cache.request_block(size)
        vb['pos'] = (-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)
        return [vb]

    def update_cache(self, shape, arg_name, value):
        self.datasets[shape][0][arg_name] = value

    def free_finalizer(self, dataset):
        if dataset:
            dataset[0].release()
            dataset.clear()

    def render(self):
        camera = get_current_ogl().manager.window.devices.cameras.current
        # update camera properties
        for block in self.__vbo.cache.blocks:
            block['near'] = camera.near_clipping_face[:3].T
            block['far'] = camera.far_clipping_face[:3].T
        self.__vbo.push_cache()

        self.__prgrm.uniforms['PM'] = camera.body.PM
        self.__prgrm.uniforms['VM'] = camera.tripod.VM
        self.__prgrm.push_uniforms()

        with self.__prgrm:
            with self.__vao:
                gl.glDrawArrays(gl.GL_QUADS, 0, 4)

import os
import OpenGL.GL as gl

import ckernel.render_context.opengl_context.meta_entities as meta
from ckernel.render_context.opengl_context.context_stack import get_current_ogl

from .base import Renderer


class GroundRenderer(Renderer):
    """
    draw infinite ground
    """
    __this_dir = os.path.dirname(__file__)
    __prgrm = meta.MetaPrgrm(vrtx_path=os.path.join(__this_dir, '../renderers/shaders/ground_vrtx_shdr.glsl'),
                             frgm_path=os.path.join(__this_dir, '../renderers/shaders/ground_frgm_shdr.glsl'))

    def __init__(self):
        self.__vbo = self.__prgrm.vrtxattr_schema.create_vrtx_bffr()
        self.__vao = meta.MetaVrtxArry(self.__vbo)

    @property
    def vbo(self):
        return self.__vbo

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

import os
import OpenGL.GL as gl
import numpy as np

import ckernel.render_context.opengl_context.meta_entities as meta
from ckernel.render_context.opengl_context.context_stack import get_current_ogl

from .base import Renderer


class FlatAxisRenderer(Renderer):
    """
    draw infinite ground
    """
    __this_dir = os.path.dirname(__file__)
    __prgrm = meta.MetaPrgrm(vrtx_path=os.path.join(__this_dir, '../renderers/shaders/flataxis_vrtx_shdr.glsl'),
                             frgm_path=os.path.join(__this_dir, '../renderers/shaders/flataxis_frgm_shdr.glsl'))

    def __init__(self):
        self.__vbo = self.__prgrm.vrtxattr_schema.create_vrtx_bffr(attr_locs=(0, 1, 2, 3))
        self.__cam_vbo = self.__prgrm.vrtxattr_schema.create_vrtx_bffr(attr_locs=(4, 5))
        self.__cam_vbo_block = self.__cam_vbo.cache.request_block(size=4)
        self.__ibo = meta.MetaIndxBffr(dtype='uint')
        self.__vao = meta.MetaVrtxArry(self.__vbo, self.__cam_vbo, indx_bffr=self.__ibo)

    @property
    def vbo(self):
        return self.__vbo

    @property
    def ibo(self):
        return self.__ibo

    def render(self):
        devices = get_current_ogl().manager.window.devices
        camera = devices.cameras.current

        self.__prgrm.uniforms['PM'] = camera.body.PM
        self.__prgrm.uniforms['VM'] = camera.tripod.VM
        self.__prgrm.uniforms['near'] = camera.body.near
        self.__prgrm.uniforms['cam_ori'] = camera.tripod.plane.origin.T
        self.__prgrm.uniforms['LRBT'] = camera.body.dim[:4]
        self.__prgrm.push_uniforms()

        self.__cam_vbo_block['ncoord'] = camera.near_clipping_face.T
        self.__cam_vbo_block['fcoord'] = camera.far_clipping_face.T
        self.__cam_vbo.push_cache()

        self.__vbo.push_cache()

        gl.glDrawBuffers(1, gl.GL_COLOR_ATTACHMENT0)
        with self.__prgrm:
            with self.__vao:
                # gl.glDisable(gl.GL_DEPTH_TEST)
                gl.glDrawArrays(gl.GL_QUADS, 0, 4)
                # gl.glEnable(gl.GL_DEPTH_TEST)

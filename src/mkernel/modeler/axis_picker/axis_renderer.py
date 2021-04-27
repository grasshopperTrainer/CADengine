import os
import OpenGL.GL as gl

import ckernel.render_context.opengl_context.entities.meta as meta
from ckernel.render_context.opengl_context.context_stack import get_current_ogl

from mkernel.renderers.base import Renderer
import ctypes

class AxisRenderer(Renderer):
    """
    draw camera flat thickened axis
    """
    __this_dir = os.path.dirname(__file__)
    __prgrm = meta.MetaPrgrm(vrtx_path=os.path.join(__this_dir, 'axis_vrtx_shdr.glsl'),
                             frgm_path=os.path.join(__this_dir, 'axis_frgm_shdr.glsl'))

    def __init__(self):
        self.__vbo = self.__prgrm.vrtx_attr_schema.create_vrtx_bffr(attr_locs=(0, 1, 2, 3, 4))

        self.__vbo_shared = self.__prgrm.vrtx_attr_schema.create_vrtx_bffr(attr_locs=(5, 6))
        self.__vbo_shared_block = self.__vbo_shared.cache.request_block(size=4)

        self.__ibo = meta.MetaIndxBffr(dtype='uint')
        self.__vao = meta.MetaVrtxArry(self.__vbo, self.__vbo_shared, indx_bffr=self.__ibo)

    @property
    def vbo(self):
        return self.__vbo

    @property
    def ibo(self):
        return self.__ibo

    def render(self):
        if not self.__ibo.cache.active_size:
            return

        devices = get_current_ogl().manager.window.devices
        camera = devices.cameras.current

        self.__prgrm.uniforms['PM'] = camera.body.PM
        self.__prgrm.uniforms['VM'] = camera.tripod.VM
        self.__prgrm.uniforms['near'] = camera.body.near
        self.__prgrm.uniforms['cam_ori'] = camera.tripod.plane.origin.T
        self.__prgrm.uniforms['LRBT'] = camera.body.dim[:4]
        self.__prgrm.push_uniforms()

        self.__vbo_shared_block['ncoord'] = camera.near_clipping_face.T
        self.__vbo_shared_block['fcoord'] = camera.far_clipping_face.T
        self.__vbo_shared.push_cache()

        self.__vbo.push_cache()

        with self.__prgrm:
            with self.__vao:
                gl.glDrawArrays(gl.GL_QUADS, 0, self.__ibo.cache.active_size)
                # gl.glDrawElements(gl.GL_QUADS,
                #                   self.__ibo.cache.active_size,
                #                   self.__ibo.cache.gldtype[0],
                #                   ctypes.c_void_p(0))
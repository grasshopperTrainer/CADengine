import numpy as np

from .base import Renderer
import ckernel.render_context.opengl_context.entities.meta as meta
from .base import get_shader_fullpath


class BrepRenderer(Renderer):

    __vrtx_vbo = meta.MetaVrtxBffr(attr_desc=np.dtype([('coord', 'f4', 4), ]), attr_locs=(0,))
    __pnt_vbo = meta.MetaVrtxBffr(attr_desc=np.dtype([('clr', 'f4', 4), ('dia', 'f4')]), attr_locs=(1, 2))

    __pnt_prgrm = meta.MetaPrgrm(
        vrtx_path=get_shader_fullpath('shaders/pnts/pntCir_vrtx_shdr.glsl'),
        frgm_path=get_shader_fullpath('shaders/pnts/pntCir_frgm_shdr.glsl'))

    def __init__(self):
        self.__pnt_ibo = meta.MetaIndxBffr(dtype='uint')
        self.__pnt_vao = meta.MetaVrtxArry(
            self.__vrtx_vbo,
            self.__pnt_vbo,
            indx_bffr=self.__pnt_ibo)

    @property
    def vrtx_vbo(self):
        return self.__vrtx_vbo

    @property
    def pnt_vbo(self):
        return self.__pnt_vbo

    @property
    def pnt_ibo(self):
        return self.__pnt_ibo

    def render(self):
        self.__vrtx_vbo.push_cache()
        # self.__render_pnt()
    #
    # def __render_pnt(self):
    #     self.__pnt_vbo.push_cache()
    #     self.__pnt_ibo.push_cache()
    #     with self.__pnt_vao:
    #         with self.__pnt_prgrm as prgrm:
    #             window = get_current_ogl().manager.window
    #             camera = window.devices.cameras.current
    #             self.__pnt_prgrm.uniforms['PM'] = camera.body.PM
    #             self.__pnt_prgrm.uniforms['VM'] = camera.tripod.VM
    #             self.__pnt_prgrm.uniforms['MM'] = np.eye(4)
    #             pane = window.devices.panes.current
    #             self.__pnt_prgrm.uniforms['VPP'] = *pane.pos, *pane.size
    #             self.__pnt_prgrm.push_uniforms()
    #
    #             gl.glDrawElements(gl.GL_POINTS,
    #                               self.__pnt_ibo.cache.active_size,
    #                               self.__pnt_ibo.cache.gldtype[0],
    #                               ct.c_void_p(0))
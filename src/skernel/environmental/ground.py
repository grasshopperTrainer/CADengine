import os
import ckernel.render_context.opengl_context.meta_entities as meta
from ckernel.render_context.opengl_context.context_stack import get_current_ogl
import OpenGL.GL as gl


class Ground:
    """
    draw infinite ground
    """
    __this_dir = os.path.dirname(__file__)
    __prgrm = meta.MetaPrgrm(vrtx_path=os.path.join(__this_dir, 'ground_vrtx_shdr.glsl'),
                             frgm_path=os.path.join(__this_dir, 'ground_frgm_shdr.glsl'))

    def __init__(self, color):
        self.__vbo = self.__prgrm.vrtxattr_schema.create_vrtx_bffr()
        self.__vao = meta.MetaVrtxArry(self.__vbo)
        self.__block = self.__vbo.cache.request_block(size=4)
        l = 1
        self.__block['pos'] = (-l, -l, 0), (l, -l, 0), (l, l, 0), (-l, l, 0)    # cover whole NDC

        self.__color = color
        self.__block['clr'] = color

    @property
    def clr(self):
        return self.__color

    @clr.setter
    def clr(self, v):
        self.__color = v
        self.__block['clr'] = v

    def render(self, camera):
        # update camera properties
        self.__block['near'] = camera.near_clipping_face[:3].T
        self.__block['far'] = camera.far_clipping_face[:3].T
        self.__vbo.push_cache()

        self.__prgrm.uniforms['PM'] = camera.body.PM
        self.__prgrm.uniforms['VM'] = camera.tripod.VM
        self.__prgrm.push_uniforms()

        with self.__prgrm:
            with self.__vao:
                gl.glDrawArrays(gl.GL_QUADS, 0, 4)

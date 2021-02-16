from .base import OGLMetaEntity
from ..ogl_entities import _FrameBffr
import ckernel.render_context.opengl_context.opengl_hooker as gl


class MetaFrameBffr(OGLMetaEntity):
    def _create_entity(self):
        return gl.glGenFramebuffers(1)


class MetaRenderBffr(OGLMetaEntity):
    def _create_entity(self):
        return gl.glGenRenderbuffers(1)


from .base import OGLMetaEntity
import ckernel.render_context.opengl_context.opengl_hooker as gl


class MetaTexture(OGLMetaEntity):
    def __init__(self):
        pass

    def _create_entity(self):
        return gl.glGenTextures(1)
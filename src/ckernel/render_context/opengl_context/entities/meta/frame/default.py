import weakref as wr

from .base import MetaFrameBffr
from ckernel.render_context.opengl_context.entities.ogl_entities import _FrameBffr
import ckernel.render_context.opengl_context.opengl_hooker as gl
from ckernel.render_context.opengl_context.entities.draw_bffr import DrawBffr


class DefaultFrameBffr(MetaFrameBffr):
    def __init__(self, window):
        """
        placeholder for a render surface's default frame buffer
        """
        self.__window = wr.ref(window)
        self.__concrete = _FrameBffr(0, gl.GL_FRAMEBUFFER)
        self._draw_bffr = DrawBffr([])

    @property
    def size(self):
        return self.__window().glyph.size

    @property
    def textures(self):
        return ()

    @property
    def color_attachments(self):
        return ()

    def _create_entity(self):
        return self.__concrete


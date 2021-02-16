import weakref as wr

from global_tools.enum import enum
import ckernel.render_context.opengl_context.opengl_hooker as gl


from gkernel.dtype.geometric.primitive import Pnt
from gkernel.dtype.nongeometric.matrix.primitive import ScaleMat

from wkernel.glyph import GlyphNode, GlyphInterface
from ._base import RenderDevice, RenderDeviceManager



class FrameFactory:
    def __init__(self, manager):
        self.__manager = wr.ref(manager)
        self.__textures = []

    class TEXTURE(enum):
        class TARGET(enum):
            D1 = enum.prop(gl.GL_TEXTURE_1D)
            D2 = enum.prop(gl.GL_TEXTURE_2D)
            D3 = enum.prop(gl.GL_TEXTURE_3D)

    def append_texture(self, target):
        """
        append texture

        ! texture will be treated with attachment index of given order
        :return:
        """


    def create(self):
        frame = None
        self.__manager()._append_device(frame)


class Frame(RenderDevice):
    pass


class FrameManager(RenderDeviceManager):
    def __init__(self, device_master):
        super().__init__(device_master)
        # no default device?

    @property
    def device_type(self):
        return Frame

    @property
    def factory(self):
        return FrameFactory(self)
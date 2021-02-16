import weakref as wr
import numpy as np
from global_tools.enum import enum
import ckernel.render_context.opengl_context.opengl_hooker as gl
import ckernel.render_context.opengl_context.meta_entities as meta

from gkernel.dtype.geometric.primitive import Pnt
from gkernel.dtype.nongeometric.matrix.primitive import ScaleMat

from wkernel.glyph import GlyphNode, GlyphInterface
from ._base import RenderDevice, RenderDeviceManager


class FrameFactory:
    def __init__(self, manager):
        self.__manager = wr.ref(manager)
        self.__size = None
        self.__textures = []
        self.__render_buffer = None

    @enum
    class TEXTURE:
        @enum
        class TARGET:
            ONE_D = enum.prop(gl.GL_TEXTURE_1D)
            TWO_D = enum.prop(gl.GL_TEXTURE_2D)
            THREE_D = enum.prop(gl.GL_TEXTURE_3D)
            # else not supported yet

        @enum
        class FORMAT:
            DEPTH_COMPONENT = enum.prop(gl.GL_DEPTH_COMPONENT)
            DEPTH_STENCIL = enum.prop(gl.GL_DEPTH_STENCIL)
            RED = enum.prop(gl.GL_RED)
            RG = enum.prop(gl.GL_RG)
            RGB = enum.prop(gl.GL_RGB)
            RGBA = enum.prop(gl.GL_RGBA)
            # else not supported yet

    @enum
    class RENDER:
        @enum
        class DEPTH:
            D16 = enum.prop(gl.GL_DEPTH_COMPONENT16)
            D24 = enum.prop(gl.GL_DEPTH_COMPONENT24)
            D32F = enum.prop(gl.GL_DEPTH_COMPONENT32F)

        @enum
        class STENCIL:
            INDEX8 = enum.prop(gl.GL_STENCIL_INDEX8)

        @enum
        class DEPTH_STENCIL:
            D24_S8 = enum.prop(gl.GL_DEPTH24_STENCIL8)
            D32F_S8 = enum.prop(gl.GL_DEPTH32F_STENCIL8)

        def COLOR(self, idx):
            return eval(f"gl.GL_COLOR_ATTACHMENT{idx}")

    def append_texture(self, target, format, width, height):
        """
        append texture

        ! texture will be treated with attachment index of given order
        :param target: target e.g. TEXTURE.TARGET.TWO_D
        :param format: internal format
        :return:
        """
        self.__textures.append(meta.MetaTexture(target, format, width, height))
        return self

    def set_render_buffer(self, format, width, height):
        """
        add render buffer

        :return:
        """
        # only one render buffer possible?
        self.__render_buffer = meta.MetaRenderBffr(format, width, height)

    def create(self):
        """
        create new meta frame

        :return:
        """
        if not (self.__textures or self.__render_buffer):
            raise ValueError('not enough properties given')

        # check contradiction in color attachment index
        if self.__render_buffer:
            low, high = int(gl.GL_COLOR_ATTACHMENT0), int(gl.GL_COLOR_ATTACHMENT31)
            iformat = int(self.__render_buffer.iformat)
            if low <= iformat <= high and iformat < low + len(self.__textures):
                raise ValueError('render buffer cant have given color attachment index')

        frame_bffr = meta.MetaFrameBffr(*self.__textures, render_buffer=self.__render_buffer)

        manager = self.__manager()
        frame = Frame(manager, frame_bffr)
        manager._appendnew_device(Frame(manager, frame_bffr))
        return frame

class Frame(RenderDevice):

    def __init__(self, manager, frame_bffr):
        super().__init__(manager)
        self.__frame_bffr = frame_bffr

    def __enter__(self):
        """
        1. bind frame buffer
        2. record current device
        :return:
        """
        self.__frame_bffr.bind()  # binding for ogl operations
        return super().__enter__()  # recording current device

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self.__frame_bffr.get_concrete().unbind()


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

from global_tools.enum import enum
import ckernel.render_context.opengl_context.opengl_hooker as gl


class DrawBufferFormats:
    @enum
    class COLOR:
        RED = enum.prop(gl.GL_RED)
        RG = enum.prop(gl.GL_RG)
        RGB = enum.prop(gl.GL_RGB)
        RGBA = enum.prop(gl.GL_RGBA)
        # ATTACHMENT0 = enum.prop(gl.GL_COLOR_ATTACHMENT0)
        # ATTACHMENT1 = enum.prop(gl.GL_COLOR_ATTACHMENT1)
        # ATTACHMENT2 = enum.prop(gl.GL_COLOR_ATTACHMENT2)
        # ATTACHMENT3 = enum.prop(gl.GL_COLOR_ATTACHMENT3)
        # ATTACHMENT4 = enum.prop(gl.GL_COLOR_ATTACHMENT4)
        # ATTACHMENT5 = enum.prop(gl.GL_COLOR_ATTACHMENT5)
        # ATTACHMENT6 = enum.prop(gl.GL_COLOR_ATTACHMENT6)
        # ATTACHMENT7 = enum.prop(gl.GL_COLOR_ATTACHMENT7)
        # ATTACHMENT8 = enum.prop(gl.GL_COLOR_ATTACHMENT8)
        # ATTACHMENT9 = enum.prop(gl.GL_COLOR_ATTACHMENT9)
        # ATTACHMENT10 = enum.prop(gl.GL_COLOR_ATTACHMENT10)
        # ATTACHMENT11 = enum.prop(gl.GL_COLOR_ATTACHMENT11)
        # ATTACHMENT12 = enum.prop(gl.GL_COLOR_ATTACHMENT12)
        # ATTACHMENT13 = enum.prop(gl.GL_COLOR_ATTACHMENT13)
        # ATTACHMENT14 = enum.prop(gl.GL_COLOR_ATTACHMENT14)
        # ATTACHMENT15 = enum.prop(gl.GL_COLOR_ATTACHMENT15)
        # ATTACHMENT16 = enum.prop(gl.GL_COLOR_ATTACHMENT16)
        # ATTACHMENT17 = enum.prop(gl.GL_COLOR_ATTACHMENT17)
        # ATTACHMENT18 = enum.prop(gl.GL_COLOR_ATTACHMENT18)
        # ATTACHMENT19 = enum.prop(gl.GL_COLOR_ATTACHMENT19)
        # ATTACHMENT20 = enum.prop(gl.GL_COLOR_ATTACHMENT20)
        # ATTACHMENT21 = enum.prop(gl.GL_COLOR_ATTACHMENT21)
        # ATTACHMENT22 = enum.prop(gl.GL_COLOR_ATTACHMENT22)
        # ATTACHMENT23 = enum.prop(gl.GL_COLOR_ATTACHMENT23)
        # ATTACHMENT24 = enum.prop(gl.GL_COLOR_ATTACHMENT24)
        # ATTACHMENT25 = enum.prop(gl.GL_COLOR_ATTACHMENT25)
        # ATTACHMENT26 = enum.prop(gl.GL_COLOR_ATTACHMENT26)
        # ATTACHMENT27 = enum.prop(gl.GL_COLOR_ATTACHMENT27)
        # ATTACHMENT28 = enum.prop(gl.GL_COLOR_ATTACHMENT28)
        # ATTACHMENT29 = enum.prop(gl.GL_COLOR_ATTACHMENT29)
        # ATTACHMENT30 = enum.prop(gl.GL_COLOR_ATTACHMENT30)
        # ATTACHMENT31 = enum.prop(gl.GL_COLOR_ATTACHMENT31)

    @enum
    class DEPTH:
        BASE = enum.prop(gl.GL_DEPTH_COMPONENT)
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
from global_tools.enum import enum
import ckernel.render_context.opengl_context.opengl_hooker as gl


class RenderBufferTarget:
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
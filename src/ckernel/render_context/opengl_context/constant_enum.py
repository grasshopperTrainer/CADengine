from global_tools.enum import enum
import ckernel.render_context.opengl_context.opengl_hooker as gl


# class OGLENUM:
#     pass

@enum
class TextureTargets:
    ONE_D = gl.GL_TEXTURE_1D
    TWO_D = gl.GL_TEXTURE_2D
    THREE_D = gl.GL_TEXTURE_3D

@enum
class DrawTargetFormats:
    @enum
    class COLOR:
        @enum
        class RED:
            RED = gl.GL_RED
            R8 = gl.GL_R8
            R8 = gl.GL_R8
            R8_SNORM = gl.GL_R8_SNORM
            R16 = gl.GL_R16
            R16F = gl.GL_R16F
            R32F = gl.GL_R32F
            R8I = gl.GL_R8I
            R8UI = gl.GL_R8UI
            R16I = gl.GL_R16I
            R16UI = gl.GL_R16UI
            R32I = gl.GL_R32I
            R32UI = gl.GL_R32UI

        @enum
        class RG:
            RG = gl.GL_RG
            R16_SNORM = gl.GL_R16_SNORM
            RG8 = gl.GL_RG8
            RG8_SNORM = gl.GL_RG8_SNORM
            RG16 = gl.GL_RG16
            RG16_SNORM = gl.GL_RG16_SNORM
            RG16F = gl.GL_RG16F
            RG32F = gl.GL_RG32F
            RG8I = gl.GL_RG8I
            RG8UI = gl.GL_RG8UI
            RG16I = gl.GL_RG16I
            RG16UI = gl.GL_RG16UI
            RG32I = gl.GL_RG32I
            RG32UI = gl.GL_RG32UI

        @enum
        class RGB:
            RGB = gl.GL_RGB
            R3_G3_B2 = gl.GL_R3_G3_B2
            RGB4 = gl.GL_RGB4
            RGB5 = gl.GL_RGB5
            RGB8 = gl.GL_RGB8
            RGB8_SNORM = gl.GL_RGB8_SNORM
            RGB10 = gl.GL_RGB10
            RGB12 = gl.GL_RGB12
            RGB16_SNORM = gl.GL_RGB16_SNORM
            RGBA2 = gl.GL_RGBA2
            RGBA4 = gl.GL_RGBA4
            SRGB8 = gl.GL_SRGB8
            RGB16F = gl.GL_RGB16F
            RGB32F = gl.GL_RGB32F
            R11F_G11F_B10F = gl.GL_R11F_G11F_B10F
            RGB9_E5 = gl.GL_RGB9_E5
            RGB8I = gl.GL_RGB8I
            RGB8UI = gl.GL_RGB8UI
            RGB16I = gl.GL_RGB16I
            RGB16UI = gl.GL_RGB16UI
            RGB32I = gl.GL_RGB32I
            RGB32UI = gl.GL_RGB32UI

        @enum
        class RGBA:
            RGBA = gl.GL_RGBA
            RGB5_A1 = gl.GL_RGB5_A1
            RGBA8 = gl.GL_RGBA8
            RGBA8_SNORM = gl.GL_RGBA8_SNORM
            RGB10_A2 = gl.GL_RGB10_A2
            RGB10_A2UI = gl.GL_RGB10_A2UI
            RGBA12 = gl.GL_RGBA12
            RGBA16 = gl.GL_RGBA16
            SRGB8_ALPHA8 = gl.GL_SRGB8_ALPHA8
            RGBA16F = gl.GL_RGBA16F
            RGBA32F = gl.GL_RGBA32F
            RGBA8I = gl.GL_RGBA8I
            RGBA8UI = gl.GL_RGBA8UI
            RGBA16I = gl.GL_RGBA16I
            RGBA16UI = gl.GL_RGBA16UI
            RGBA32I = gl.GL_RGBA32I
            RGBA32UI = gl.GL_RGBA32UI
    @enum
    class NONECOLOR:
        @enum
        class DEPTH:
            DEPTH_COMPONENT = gl.GL_DEPTH_COMPONENT
            DEPTH_COMPONENT16 = gl.GL_DEPTH_COMPONENT16
            DEPTH_COMPONENT24 = gl.GL_DEPTH_COMPONENT24
            DEPTH_COMPONENT32F = gl.GL_DEPTH_COMPONENT32F

        @enum
        class DEPTH_STENCIL:
            DEPTH_STENCIL = gl.GL_DEPTH_STENCIL
            DEPTH24_STENCIL8 = gl.GL_DEPTH24_STENCIL8
            DEPTH32F_STENCIL8 = gl.GL_DEPTH32F_STENCIL8

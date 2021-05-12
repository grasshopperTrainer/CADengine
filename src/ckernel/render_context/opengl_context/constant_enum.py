from global_tools.enum import enum, EnumAttr
import ckernel.render_context.opengl_context.opengl_hooker as gl


# class OGLENUM:
#     pass

@enum
class TextureTargets:
    ONE_D = gl.GL_TEXTURE_1D
    TWO_D = gl.GL_TEXTURE_2D
    THREE_D = gl.GL_TEXTURE_3D

@enum
class TextureFormats:
    @enum
    class COLOR:
        @enum
        class RED:
            RED = EnumAttr(rep_val=gl.GL_RED, bitpattern=(8,))
            R8 = EnumAttr(rep_val=gl.GL_R8, bitpattern=(8,))
            R8_SNORM = EnumAttr(rep_val=gl.GL_R8_SNORM, bitpattern=(8, ))
            R16 = EnumAttr(rep_val=gl.GL_R16, bitpattern=(16, ))
            R16F = EnumAttr(rep_val=gl.GL_R16F, bitpattern=(16, ))
            R32F = EnumAttr(rep_val=gl.GL_R32F, bitpattern=(16, ))
            R8I = EnumAttr(rep_val=gl.GL_R8I, bitpattern=(8, ))
            R8UI = EnumAttr(rep_val=gl.GL_R8UI, bitpattern=(8, ))
            R16I = EnumAttr(rep_val=gl.GL_R16I, bitpattern=(16, ))
            R16UI = EnumAttr(rep_val=gl.GL_R16UI, bitpattern=(16, ))
            R32I = EnumAttr(rep_val=gl.GL_R32I, bitpattern=(32, ))
            R32UI = EnumAttr(rep_val=gl.GL_R32UI, bitpattern=(32, ))

        @enum
        class RG:
            RG = EnumAttr(rep_val=gl.GL_RG, bitpattern=(8, 8))
            R16_SNORM = EnumAttr(rep_val=gl.GL_R16_SNORM, bitpattern=(16, 16))
            RG8 = EnumAttr(rep_val=gl.GL_RG8, bitpattern=(8, 8))
            RG8_SNORM = EnumAttr(rep_val=gl.GL_RG8_SNORM, bitpattern=(8, 8))
            RG16 = EnumAttr(rep_val=gl.GL_RG16, bitpattern=(16, 16))
            RG16_SNORM = EnumAttr(rep_val=gl.GL_RG16_SNORM, bitpattern=(16, 16))
            RG16F = EnumAttr(rep_val=gl.GL_RG16F, bitpattern=(16, 16))
            RG32F = EnumAttr(rep_val=gl.GL_RG32F, bitpattern=(32, 32))
            RG8I = EnumAttr(rep_val=gl.GL_RG8I, bitpattern=(8, 8))
            RG8UI = EnumAttr(rep_val=gl.GL_RG8UI, bitpattern=(8, 8))
            RG16I = EnumAttr(rep_val=gl.GL_RG16I, bitpattern=(16, 16))
            RG16UI = EnumAttr(rep_val=gl.GL_RG16UI, bitpattern=(16, 16))
            RG32I = EnumAttr(rep_val=gl.GL_RG32I, bitpattern=(32, 32))
            RG32UI = EnumAttr(rep_val=gl.GL_RG32UI, bitpattern=(32, 32))


        @enum
        class RGB:
            RGB = EnumAttr(rep_val=gl.GL_RGB, bitpattern=(8, 8, 8))
            R3_G3_B2 = EnumAttr(rep_val=gl.GL_R3_G3_B2, bitpattern=(3, 3, 2))
            RGB4 = EnumAttr(rep_val=gl.GL_RGB4, bitpattern=(4, 4, 4))
            RGB5 = EnumAttr(rep_val=gl.GL_RGB5, bitpattern=(5, 5, 5))
            RGB8 = EnumAttr(rep_val=gl.GL_RGB8, bitpattern=(8, 8, 8))
            RGB8_SNORM = EnumAttr(rep_val=gl.GL_RGB8_SNORM, bitpattern=(8, 8, 8))
            RGB10 = EnumAttr(rep_val=gl.GL_RGB10, bitpattern=(10, 10, 10))
            RGB12 = EnumAttr(rep_val=gl.GL_RGB12, bitpattern=(12, 12, 12))
            RGB16_SNORM = EnumAttr(rep_val=gl.GL_RGB16_SNORM, bitpattern=(16, 16, 16))
            RGBA2 = EnumAttr(rep_val=gl.GL_RGBA2, bitpattern=(2, 2, 2))
            RGBA4 = EnumAttr(rep_val=gl.GL_RGBA4, bitpattern=(4, 4, 4))
            SRGB8 = EnumAttr(rep_val=gl.GL_SRGB8, bitpattern=(8, 8, 8))
            RGB16F = EnumAttr(rep_val=gl.GL_RGB16F, bitpattern=(16, 16, 16))
            RGB32F = EnumAttr(rep_val=gl.GL_RGB32F, bitpattern=(32, 32, 32))
            R11F_G11F_B10F = EnumAttr(rep_val=gl.GL_R11F_G11F_B10F, bitpattern=(11, 11, 10))
            RGB9_E5 = EnumAttr(rep_val=gl.GL_RGB9_E5, bitpattern=(9, 9, 9, 5))
            RGB8I = EnumAttr(rep_val=gl.GL_RGB8I, bitpattern=(8, 8, 8))
            RGB8UI = EnumAttr(rep_val=gl.GL_RGB8UI, bitpattern=(8, 8, 8))
            RGB16I = EnumAttr(rep_val=gl.GL_RGB16I, bitpattern=(16, 16, 16))
            RGB16UI = EnumAttr(rep_val=gl.GL_RGB16UI, bitpattern=(16, 16, 16))
            RGB32I = EnumAttr(rep_val=gl.GL_RGB32I, bitpattern=(32, 32, 32))
            RGB32UI = EnumAttr(rep_val=gl.GL_RGB32UI, bitpattern=(32, 32, 32))


        @enum
        class RGBA:
            RGBA = EnumAttr(rep_val=gl.GL_RGBA, bitpattern=(8, 8, 8, 8))
            RGB5_A1 = EnumAttr(rep_val=gl.GL_RGB5_A1, bitpattern=(5, 5, 5, 1))
            RGBA8 = EnumAttr(rep_val=gl.GL_RGBA8, bitpattern=(8, 8, 8, 8))
            RGBA8_SNORM = EnumAttr(rep_val=gl.GL_RGBA8_SNORM, bitpattern=(8, 8, 8, 8))
            RGB10_A2 = EnumAttr(rep_val=gl.GL_RGB10_A2, bitpattern=(10, 10, 10, 2))
            RGB10_A2UI = EnumAttr(rep_val=gl.GL_RGB10_A2UI, bitpattern=(10, 10, 10, 2))
            RGBA12 = EnumAttr(rep_val=gl.GL_RGBA12, bitpattern=(12, 12, 12, 12))
            RGBA16 = EnumAttr(rep_val=gl.GL_RGBA16, bitpattern=(16, 16, 16, 16))
            SRGB8_ALPHA8 = EnumAttr(rep_val=gl.GL_SRGB8_ALPHA8, bitpattern=(8, 8, 8, 8))
            RGBA16F = EnumAttr(rep_val=gl.GL_RGBA16F, bitpattern=(16, 16, 16, 16))
            RGBA32F = EnumAttr(rep_val=gl.GL_RGBA32F, bitpattern=(32, 32, 32, 32))
            RGBA8I = EnumAttr(rep_val=gl.GL_RGBA8I, bitpattern=(8, 8, 8, 8))
            RGBA8UI = EnumAttr(rep_val=gl.GL_RGBA8UI, bitpattern=(8, 8, 8, 8))
            RGBA16I = EnumAttr(rep_val=gl.GL_RGBA16I, bitpattern=(16, 16, 16, 16))
            RGBA16UI = EnumAttr(rep_val=gl.GL_RGBA16UI, bitpattern=(16, 16, 16, 16))
            RGBA32I = EnumAttr(rep_val=gl.GL_RGBA32I, bitpattern=(32, 32, 32, 32))
            RGBA32UI = EnumAttr(rep_val=gl.GL_RGBA32UI, bitpattern=(32, 32, 32, 32))

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

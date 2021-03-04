import numpy as np
from ckernel.render_context.opengl_context.meta_entities.base import OGLMetaEntity
import ckernel.render_context.opengl_context.opengl_hooker as gl
from global_tools.enum import enum
from .exporter import TxtrExporter


class MetaTexture(OGLMetaEntity):

    def __init__(self, target, iformat, width, height):
        self.__target = target
        self.__iformat = iformat
        self.__format = self.__iformat_to_format()
        self.__size = width, height

    def __str__(self):
        return f"<MetaTexture: {self.__target}, {self.__iformat}>"

    @property
    def iformat(self):
        return self.__iformat

    @property
    def target(self):
        return self.__target

    @property
    def size(self):
        return self.__size

    @enum
    class TARGET:
        ONE_D = enum.prop(gl.GL_TEXTURE_1D)
        TWO_D = enum.prop(gl.GL_TEXTURE_2D)
        THREE_D = enum.prop(gl.GL_TEXTURE_3D)

    def bind(self):
        super(MetaTexture, self).bind()
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)

    def _create_entity(self):
        texture = gl.glGenTextures(1)
        texture.set_target(self.__target)
        with texture:
            # data can latter be filled so make glTexImage2D part of initiation
            if self.__target in (gl.GL_TEXTURE_2D,):
                # default settings
                gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
                gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
                gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
                gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
                gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
                gl.glTexImage2D(self.__target,  # target
                                0,  # level
                                self.__iformat,  # internalformat
                                self.__size[0],  # width
                                self.__size[1],  # height
                                0,  # border
                                self.__format,  # format
                                gl.GL_UNSIGNED_BYTE,  # type
                                None)  # data
            else:
                raise NotImplementedError
        return texture

    __red_iformats = (gl.GL_RED,
                      gl.GL_R8,
                      gl.GL_R8,
                      gl.GL_R8_SNORM,
                      gl.GL_R16,
                      gl.GL_R16F,
                      gl.GL_R32F,
                      gl.GL_R8I,
                      gl.GL_R8UI,
                      gl.GL_R16I,
                      gl.GL_R16UI,
                      gl.GL_R32I,
                      gl.GL_R32UI)

    __rg_iformats = (gl.GL_RG,
                     gl.GL_R16_SNORM,
                     gl.GL_RG8,
                     gl.GL_RG8_SNORM,
                     gl.GL_RG16,
                     gl.GL_RG16_SNORM,
                     gl.GL_RG16F,
                     gl.GL_RG32F,
                     gl.GL_RG8I,
                     gl.GL_RG8UI,
                     gl.GL_RG16I,
                     gl.GL_RG16UI,
                     gl.GL_RG32I,
                     gl.GL_RG32UI)

    __rgb_iformats = (gl.GL_RGB,
                      gl.GL_R3_G3_B2,
                      gl.GL_RGB4,
                      gl.GL_RGB5,
                      gl.GL_RGB8,
                      gl.GL_RGB8_SNORM,
                      gl.GL_RGB10,
                      gl.GL_RGB12,
                      gl.GL_RGB16_SNORM,
                      gl.GL_RGBA2,
                      gl.GL_RGBA4,
                      gl.GL_SRGB8,
                      gl.GL_RGB16F,
                      gl.GL_RGB32F,
                      gl.GL_R11F_G11F_B10F,
                      gl.GL_RGB9_E5,
                      gl.GL_RGB8I,
                      gl.GL_RGB8UI,
                      gl.GL_RGB16I,
                      gl.GL_RGB16UI,
                      gl.GL_RGB32I,
                      gl.GL_RGB32UI)

    __rgba_iformats = (gl.GL_RGBA,
                       gl.GL_RGB5_A1,
                       gl.GL_RGBA8,
                       gl.GL_RGBA8_SNORM,
                       gl.GL_RGB10_A2,
                       gl.GL_RGB10_A2UI,
                       gl.GL_RGBA12,
                       gl.GL_RGBA16,
                       gl.GL_SRGB8_ALPHA8,
                       gl.GL_RGBA16F,
                       gl.GL_RGBA32F,
                       gl.GL_RGBA8I,
                       gl.GL_RGBA8UI,
                       gl.GL_RGBA16I,
                       gl.GL_RGBA16UI,
                       gl.GL_RGBA32I,
                       gl.GL_RGBA32UI)

    __depth_iformats = (gl.GL_DEPTH_COMPONENT,
                        gl.GL_DEPTH_COMPONENT16,
                        gl.GL_DEPTH_COMPONENT24,
                        gl.GL_DEPTH_COMPONENT32F)

    __depth_stencil_iformats = (gl.GL_DEPTH_STENCIL,
                                gl.GL_DEPTH24_STENCIL8,
                                gl.GL_DEPTH32F_STENCIL8)

    __iformats = {gl.GL_RED: set(__red_iformats),
                  gl.GL_RG: set(__rg_iformats),
                  gl.GL_RGB: set(__rgb_iformats),
                  gl.GL_RGBA: set(__rgba_iformats),
                  gl.GL_DEPTH_COMPONENT: set(__depth_iformats),
                  gl.GL_DEPTH_STENCIL: set(__depth_stencil_iformats)}

    def __iformat_to_format(self):
        """
        translate internal format to desired texture input format

        :return:
        """
        for base, iformats in self.__iformats.items():
            if self.__iformat in iformats:
                return base
        raise NotImplementedError

    def as_unit(self, unit):
        """
        instant unit setting

        :param unit:
        :return:
        """
        return _MetaTextureAsUnit(self, unit)

    def image_export(self, file_name: str):
        """
        export texture as an image file

        :param file_name:
        :param format:
        :return:
        """
        im_format = file_name.rsplit('.')[-1]
        if im_format in ('jpg',):
            iformat = gl.GL_BGR
            comp_size = 3
        elif im_format in ('png',):
            iformat = gl.GL_BGRA
            comp_size = 4
        else:
            raise NotImplementedError

        with self:
            gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)
            im = gl.glGetTexImage(gl.GL_TEXTURE_2D, 0, iformat, gl.GL_UNSIGNED_BYTE)
        im = np.array(tuple(im)).reshape((self.size[1], self.size[0], comp_size))
        im = np.flip(im, axis=0)
        TxtrExporter().export(file_name, im)


class _MetaTextureAsUnit:
    def __init__(self, mt, unit):
        self.__mt = mt
        self.__unit = unit

    def __enter__(self):
        gl.glActiveTexture(gl.GL_TEXTURE0 + self.__unit)
        self.__mt.bind()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__mt.unbind()

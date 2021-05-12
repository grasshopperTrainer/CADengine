import numpy as np
from ckernel.render_context.opengl_context.entities.meta.base import OGLMetaEntity
from ckernel.render_context.opengl_context.constant_enum import TextureFormats as DTF
from ckernel.render_context.opengl_context.constant_enum import TextureTargets as TT
import ckernel.render_context.opengl_context.opengl_hooker as gl
from global_tools.enum import enum
from .exporter import TxtrExporter


class MetaTexture(OGLMetaEntity):

    def __init__(self, target, iformat, width, height, name=None):
        self.__target = target
        self.__iformat = iformat
        self.__format = self.__parse_format(iformat)
        self.__size = width, height
        self.__type = self.__parse_type(iformat)
        self.__name = name

    def __str__(self):
        return f"<MetaTexture: {self.__target}, {self.__iformat}>"

    @property
    def iformat(self):
        return self.__iformat

    @property
    def target(self):
        return self.__target

    @property
    def format(self):
        return self.__format

    @property
    def type(self):
        return self.__type

    @property
    def size(self):
        return self.__size

    @property
    def name(self):
        return self.__name

    def bind(self):
        super().bind()
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)

    def _create_entity(self):
        texture = gl.glGenTextures(1)
        texture.set_target(self.__target)
        with texture:
            # data can latter be filled so make glTexImage2D part of initiation
            if self.__target == TT.TWO_D:
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
                                self.__type,  # type
                                None)  # data
            else:
                raise NotImplementedError
        return texture

    @staticmethod
    def __parse_format(iformat):
        """
        translate internal format to desired texture input format

        :return:
        """
        for _, base in (*DTF.COLOR, *DTF.NONECOLOR):
            if iformat in base:
                base = base[0]
                break

        if 'I' in str(iformat):
            return eval(f"gl.{str(base).split(' ')[0]}_INTEGER")
        return base

    @staticmethod
    def __parse_type(iformat):
        # special cases
        if iformat.val == gl.GL_RGB10_A2UI:
            return gl.GL_UNSIGNED_INT_10_10_10_2
        elif iformat.val == gl.GL_RGB10_A2:
            return gl.GL_UNSIGNED_INT_10_10_10_2

        if 'UI' in str(iformat):
            return gl.GL_UNSIGNED_INT
        elif 'I' in str(iformat):
            return gl.GL_INT
        elif 'F' in str(iformat):
            return gl.GL_FLOAT
        else:
            return gl.GL_UNSIGNED_BYTE

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
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)

        self.__mt.enter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__mt.exit()

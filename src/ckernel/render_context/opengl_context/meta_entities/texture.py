from .base import OGLMetaEntity
import ckernel.render_context.opengl_context.opengl_hooker as gl
from global_tools.enum import enum


class MetaTexture(OGLMetaEntity):
    def __init__(self, target, iformat, width, height):
        self.__target = target
        self.__iformat = iformat
        self.__format = self.__iformat_to_format()
        self.__size = width, height

    @property
    def target(self):
        return self.__target

    @enum
    class TARGET:
        ONE_D = enum.prop(gl.GL_TEXTURE_1D)
        TWO_D = enum.prop(gl.GL_TEXTURE_2D)
        THREE_D = enum.prop(gl.GL_TEXTURE_3D)

    def _create_entity(self):
        texture = gl.glGenTextures(1)
        texture.set_target(self.__target)
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
        with texture as t:
            # data can latter be filled so make glTexImage2D part of initiation
            if self.__target in (gl.GL_TEXTURE_2D,):
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

    def __iformat_to_format(self):
        """
        translate internal format to desired texture input format

        :return:
        """
        if self.__iformat == gl.GL_RGB:
            return gl.GL_RGB
        elif self.__iformat == gl.GL_RGBA:
            return gl.GL_RGBA
        else:
            raise NotImplementedError

    def _push_image(self):
        # texture.set_iformat(self.__iformat)
        # with texture:
        #     if self.__target in (gl.GL_TEXTURE_2D,):
        #         gl.glTexImage2D(target=self.__target,
        #                         level=0,
        #                         internalformat=self.__iformat,
        #                         width=self.__size[0],
        #                         height=self.__size[1],
        #                         border=0,
        #                         format=gl.GL_RGB,
        #                         type=gl.GL_UNSIGNED_INT,
        #                         data=None)
        #         raise
        #     else:
        #         raise NotImplementedError
        raise

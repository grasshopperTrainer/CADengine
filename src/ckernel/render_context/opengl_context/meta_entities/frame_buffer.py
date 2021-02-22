from .base import OGLMetaEntity
from ..ogl_entities import _FrameBffr
import ckernel.render_context.opengl_context.opengl_hooker as gl
from .texture import MetaTexture
from ..constant_enum import RenderBufferTarget


class MetaFrameBffr(OGLMetaEntity):

    def __init__(self, *textures, render_buffer=None):
        """

        ! textures order index will be used as attachment index
        :param textures: (MetaTexture, ...)
        :param render_buffer: MetaRenderBffr
        """
        self.__textures = textures
        self.__render_buffer = render_buffer

    def __str__(self):
        return f"<MetaFrameBffr >"

    @property
    def size(self):
        return self.__textures[0].size

    def _create_entity(self):
        if not (self.__textures or self.__render_buffer):
            raise ValueError('not enough properties given')

        fb = gl.glGenFramebuffers(1, gl.GL_FRAMEBUFFER)
        fb.set_target(gl.GL_FRAMEBUFFER)
        with fb:
            # deal with textures
            # ! give attantion to how attachment index is given
            for i, texture in enumerate(self.__textures):
                # with texture as t:
                if texture.target == gl.GL_TEXTURE_2D:
                    gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER,  # target
                                              eval(f"gl.GL_COLOR_ATTACHMENT{i}"),  # attachment
                                              texture.target,  # textarget
                                              texture.get_concrete(),  # texture
                                              0)  # level
                else:
                    raise NotImplementedError

            if self.__render_buffer:
                gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER,  # target
                                             self.__iformat_to_attachment(self.__render_buffer.iformat),  # attachment
                                             gl.GL_RENDERBUFFER,  # renderbuffertarget
                                             self.__render_buffer.get_concrete())  # renderbuffer
            # check texture binding
            if gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER) != gl.GL_FRAMEBUFFER_COMPLETE:
                raise Exception('FrameBuffer linking error')

        return fb

    def __iformat_to_attachment(self, iformat):
        if iformat in RenderBufferTarget.DEPTH_STENCIL:
            return gl.GL_DEPTH_STENCIL_ATTACHMENT
        else:
            raise TypeError

    def get_texture_attachment(self, idx):
        """
        return texture of given color attachment

        :param idx:
        :return:
        """
        return self.__textures[idx]


class MetaRenderBffr(OGLMetaEntity):
    def __init__(self, iformat, width, height):
        self.__iformat = iformat
        self.__size = width, height

    @property
    def iformat(self):
        return self.__iformat

    def _create_entity(self):
        bffr = gl.glGenRenderbuffers(1)
        with bffr:
            gl.glRenderbufferStorage(gl.GL_RENDERBUFFER,  # target
                                     self.__iformat,  # internalformat
                                     self.__size[0],  # width
                                     self.__size[1])  # height
        return bffr

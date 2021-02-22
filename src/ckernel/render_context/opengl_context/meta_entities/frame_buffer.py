from .base import OGLMetaEntity
from ..ogl_entities import _FrameBffr
import ckernel.render_context.opengl_context.opengl_hooker as gl
from .texture import MetaTexture
from ..constant_enum import RenderBufferTarget


class MetaFrameBffr(OGLMetaEntity):

    def __init__(self, *attachments, locs):
        """

        :param attachments: MetaTexture or MetaRenderBffr
        :param locs: (int, ...) indx value that will be translated into GL_COLOR_ATTACHMENT{indx}
        """
        if len(attachments) != len(locs):
            raise Exception('all locations for attachment has to be given, for that does not have location set `None`')

        __locs = set()
        self.__textures = {}
        self.__render_buffer = []
        for a, l in zip(attachments, locs):
            if l is not None:
                if l in __locs:
                    raise ValueError('attachment location value has to be unique')
                else:
                    __locs.add(l)
            if isinstance(a, MetaTexture):
                self.__textures[l] = a
            elif isinstance(a, MetaRenderBffr):
                self.__render_buffer.append((a, l))
            else:
                raise TypeError

        self.__color_attachment_locs = []
        for i in __locs:
            self.__color_attachment_locs.append(eval(f"gl.GL_COLOR_ATTACHMENT{i}"))

    def __str__(self):
        return f"<MetaFrameBffr >"

    @property
    def size(self):
        """
        ! this isnt so good

        :return:
        """
        return self.__textures[0].size

    def _create_entity(self):
        if not (self.__textures or self.__render_buffer):
            raise ValueError('not enough properties given')

        fb = gl.glGenFramebuffers(1, gl.GL_FRAMEBUFFER)
        fb.set_target(gl.GL_FRAMEBUFFER)
        with fb:
            # deal with textures
            # ! give attantion to how attachment index is given
            for i, texture in self.__textures.items():
                if texture.target == gl.GL_TEXTURE_2D:
                    gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER,  # target
                                              eval(f"gl.GL_COLOR_ATTACHMENT{i}"),  # attachment
                                              texture.target,  # textarget
                                              texture.get_concrete(),  # texture
                                              0)  # level
                else:
                    raise NotImplementedError

            for rb, i in self.__render_buffer:
                if gl.GL_COLOR_ATTACHMENT0 <= rb.iformat <= gl.GL_COLOR_ATTACHMENT31:
                    if i is None:
                        raise ValueError('color attachment location for frame buffer not given')
                else:
                    if i is not None:
                        raise ValueError('given location cant be resolved')
                    gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER,  # target
                                                 self.__iformat_to_attachment(rb.iformat),  # attachment
                                                 gl.GL_RENDERBUFFER,  # renderbuffertarget
                                                 rb.get_concrete())  # renderbuffer
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

    def bind(self):
        """
        extended to use multiple color attachment

        :return:
        """
        super().bind()
        gl.glDrawBuffers(len(self.__color_attachment_locs), self.__color_attachment_locs)


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

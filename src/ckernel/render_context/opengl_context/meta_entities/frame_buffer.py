from .base import OGLMetaEntity
import ckernel.render_context.opengl_context.opengl_hooker as gl
from ckernel.render_context.opengl_context.meta_entities.txtr.body import MetaTexture
from ..constant_enum import DrawTargetFormats as DTF
from ..constant_enum import TextureTargets as TT


class MetaFrameBffr(OGLMetaEntity):

    def __init__(self, *attachments, tids):
        """

        :param attachments: MetaTexture or MetaRenderBffr
        :param tids: int or str, semantic texture ids
                    integer - color attachment
                    'd','ds' - depth and depth-stencil
        """
        for a in attachments:
            if not isinstance(a, (MetaTexture, MetaRenderBffr)):
                raise TypeError
        if len(attachments) != len(tids):
            raise Exception('all locations for attachment has to be given, for that does not have location set `None`')
        if len(set(tids)) != len(tids):
            raise ValueError('texture ids has to be unique')
        for tid in tids:
            if isinstance(tid, str):
                if tid not in ('d', 'ds'):
                    raise ValueError
            elif not isinstance(tid, int):
                raise TypeError

        self.__attachments = {t: a for a, t in zip(attachments, tids)}
        self.__color_attachment_locs = [eval(f"gl.GL_COLOR_ATTACHMENT{i}") for i in tids if isinstance(i, int)]

    def __str__(self):
        return f"<MetaFrameBffr >"

    @property
    def size(self):
        """
        ! this isnt so good

        :return:
        """
        return self.__textures[0].size

    @property
    def textures(self):
        pass

    def _create_entity(self):
        if not self.__attachments:
            raise ValueError('not enough properties given')

        fb = gl.glGenFramebuffers(1, gl.GL_FRAMEBUFFER)
        fb.set_target(gl.GL_FRAMEBUFFER)
        with fb:
            for tid, att in self.__attachments.items():
                if isinstance(att, MetaTexture):
                    # deal with textures
                    if att.target in TT:
                        # find attachment
                        if DTF.COLOR.has_member(att.iformat):
                            attachment = eval(f'gl.GL_COLOR_ATTACHMENT{tid}')
                        else:
                            attachment = self.__iformat_to_attachment(att.iformat)

                        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER,  # target
                                                  attachment,  # attachment
                                                  att.target,  # textarget
                                                  att.get_concrete(),  # texture
                                                  0)  # level
                    else:
                        raise NotImplementedError
                else:
                    if gl.GL_COLOR_ATTACHMENT0 <= att.iformat <= gl.GL_COLOR_ATTACHMENT31:
                        if tid is None:
                            raise ValueError('color attachment location for frame buffer not given')
                    else:
                        if tid is not None:
                            raise ValueError('given location cant be resolved')
                        gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER,  # target
                                                     self.__iformat_to_attachment(att.iformat),  # attachment
                                                     gl.GL_RENDERBUFFER,  # renderbuffertarget
                                                     att.get_concrete())  # renderbuffer
            # check texture binding
            if gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER) != gl.GL_FRAMEBUFFER_COMPLETE:
                raise Exception('FrameBuffer linking error')

        return fb

    @staticmethod
    def __iformat_to_attachment(iformat):
        if iformat in DTF.NONECOLOR.DEPTH:
            return gl.GL_DEPTH_ATTACHMENT
        elif iformat in DTF.NONECOLOR.DEPTH_STENCIL:
            return gl.GL_DEPTH_STENCIL_ATTACHMENT
        else:
            raise TypeError

    def get_attachment(self, tid) -> MetaTexture:
        """
        return texture of given color attachment

        :param tid: texture id, e.g.
                    0, 1 - integers for color attachment
                    'd' - depth attachment
                    'ds' - depth stencil attachment
        :return:
        """
        return self.__attachments[tid]

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

from .base import OGLMetaEntity
import ckernel.render_context.opengl_context.opengl_hooker as gl
from ckernel.render_context.opengl_context.meta_entities.txtr.body import MetaTexture
from ..constant_enum import DrawTargetFormats as DTF
from ..constant_enum import TextureTargets as TT


class MetaFrameBffr(OGLMetaEntity):

    def __init__(self, *attachments, aids):
        """

        :param attachments: MetaTexture or MetaRenderBffr
        :param aids: int or str, location id, semantic texture ids
                    integer - color attachment
                    'd','ds' - depth and depth-stencil
        """
        # check attachment and location pair
        if len(attachments) != len(aids):
            raise Exception('all locations for attachment has to be given, for that does not have location set `None`')

        checked = {}
        # check aid syntax
        for att, aid in zip(attachments, aids):
            if isinstance(att, MetaTexture):
                if not (isinstance(aid, int) or aid in ('d', 'ds')):
                    raise TypeError('incorrect location id')
                if aid in checked:
                    raise ValueError('aid has to be unique')
            elif isinstance(att, MetaRenderBffr):
                # if i is not None:
                #     raise TypeError('render buffer should have None aid')
                if aid in checked:
                    raise ValueError('aid has to be unique')
            else:
                raise TypeError('Attachment should pass isinstance(a, (MetaTexture, MetaRenderBffr))')
            # register for getitem
            checked[aid] = att
            if att.name is not None:
                checked[att.name] = att.name

        self.__attachments = checked
        self.__color_attachment_names = [eval(f"gl.GL_COLOR_ATTACHMENT{i}") for i in aids if isinstance(i, int)]

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
    def textures(self) -> MetaTexture:
        return self.__attachments.copy()

    def _create_entity(self):
        if not self.__attachments:
            raise ValueError('not enough properties given')

        fb = gl.glGenFramebuffers(1, gl.GL_FRAMEBUFFER)
        fb.set_target(gl.GL_FRAMEBUFFER)
        with fb:
            for aid, att in self.__attachments.items():
                # textures then render buffers
                if isinstance(att, MetaTexture):
                    if att.target in TT:
                        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER,  # target
                                                  self.__iformat_to_attachment(att.iformat, aid),  # attachment
                                                  att.target,  # target
                                                  att.get_concrete(),  # texture
                                                  0)  # level
                    else:
                        raise NotImplementedError
                else:
                    gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER,  # target
                                                 self.__iformat_to_attachment(att.iformat, aid),  # attachment
                                                 gl.GL_RENDERBUFFER,  # renderbuffertarget
                                                 att.get_concrete())  # renderbuffer
            # check texture binding
            if gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER) != gl.GL_FRAMEBUFFER_COMPLETE:
                raise Exception('FrameBuffer linking error')

        return fb

    @staticmethod
    def __iformat_to_attachment(iformat, aid):
        """
        pick attachment

        :param iformat:
        :param aid:
        :return:
        """
        if DTF.COLOR.has_member(iformat):
            return eval(f'gl.GL_COLOR_ATTACHMENT{aid}')
        elif iformat in DTF.NONECOLOR.DEPTH:
            return gl.GL_DEPTH_ATTACHMENT
        elif iformat in DTF.NONECOLOR.DEPTH_STENCIL:
            return gl.GL_DEPTH_STENCIL_ATTACHMENT
        else:
            raise TypeError

    def get_attachment(self, aid) -> MetaTexture:
        """
        return texture of given color attachment

        :param aid: location id, e.g.
                    0, 1 - integers for color attachment
                    'd' - depth attachment
                    'ds' - depth stencil attachment
        :return:
        """
        return self.__attachments[aid]

    def bind(self):
        """
        extended to use multiple color attachment

        :return:
        """
        super().bind()
        gl.glDrawBuffers(len(self.__color_attachment_names), self.__color_attachment_names)
        # gl.glColorMaski(1, True, True, True, False)


class MetaRenderBffr(OGLMetaEntity):
    def __init__(self, iformat, width, height, name):
        self.__iformat = iformat
        self.__size = width, height
        self.__name = name

    @property
    def iformat(self):
        return self.__iformat

    @property
    def name(self):
        return self.__name

    def _create_entity(self):
        bffr = gl.glGenRenderbuffers(1)
        with bffr:
            gl.glRenderbufferStorage(gl.GL_RENDERBUFFER,  # target
                                     self.__iformat,  # internalformat
                                     self.__size[0],  # width
                                     self.__size[1])  # height
        return bffr

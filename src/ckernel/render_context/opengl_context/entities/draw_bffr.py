from ckernel.render_context.opengl_context.context_stack import get_current_ogl
import ckernel.render_context.opengl_context.opengl_hooker as gl


class DrawBffr:
    def __init__(self, aids):
        """
        bind draw buffer

        Used by `MetaFrameBffr`, and `MetaPrgrm` also to render only onto desired attachment.
        :param aids:
        """
        self.__aids = aids
        self.__color_attachments = tuple(eval(f"gl.GL_COLOR_ATTACHMENT{i}") for i in aids)

    def __len__(self):
        return len(self.__color_attachments)

    def bind(self):
        if self.__aids:
            gl.glDrawBuffers(len(self.__color_attachments), self.__color_attachments)
        else: # for default surface
            gl.glDrawBuffers(1, gl.GL_FRONT_LEFT)

    def enter(self):
        get_current_ogl().entity_stacker.push(self)
        self.bind()

    def exit(self):
        stacker = get_current_ogl().entity_stacker[self.__class__]
        stacker.pop()
        if stacker and stacker.peek() != self:
            stacker.peek().bind()


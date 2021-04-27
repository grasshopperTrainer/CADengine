from ckernel.render_context.opengl_context.context_stack import get_current_ogl
import ckernel.render_context.opengl_context.opengl_hooker as gl


class DrawBffr:
    def __init__(self, aids):
        """
        bind draw buffer

        Used by `MetaFrameBffr`, and `MetaPrgrm` also to render only onto desired attachment.
        :param aids:
        """
        self.__aids = sorted(aids)
        self.__clr_att = []
        if aids:
            ptr = 0
            for n in range(self.__aids[-1]+1):
                if self.__aids[ptr] == n:
                    self.__clr_att.append(eval(f"gl.GL_COLOR_ATTACHMENT{n}"))
                    ptr += 1
                else:
                    self.__clr_att.append(gl.GL_NONE)

    def __str__(self):
        return f"<{self.__class__.__name__} {self.__clr_att}>"

    def __len__(self):
        return len(self.__clr_att)

    def bind(self):
        if self.__aids:
            gl.glDrawBuffers(len(self.__clr_att), self.__clr_att)
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


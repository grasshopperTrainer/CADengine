from .gl_component import OpenglComponent
from .._component import *
import OpenGL.GL as opengl

class RenderComponent(OpenglComponent):
    """
    Renderable components

    Render trigered by Window._run -> Pipeline.render -> RenderComponent.render
    """

    @property
    def is_renderable(self):
        return True

    def render(self):
        raise NotImplementedError


class DrawArrayComponent(RenderComponent):
    """
    Render components of glDrawArrays()
    """
    _kind = None


class DrawTriangle(DrawArrayComponent):
    """
    glDrawArrays(GL_TRIANGLES, ...)
    """

    vrtx_arry = Input(def_val=None)
    idx_bound = Input(def_val=Bound(0, 3))
    render_attempt = Output(None)

    _kind = opengl.GL_TRIANGLES

    def __init__(self, window=None, vao=None, idx_bound=None):
        super().__init__(window)
        self.vrtx_arry = vao
        if idx_bound is not None:
            self.idx_bound = idx_bound

    def operate(self):
        self.render()
        self.render_attempt = True

    # @log_execution
    def render(self):
        self.gl.glBindVertexArray(self.vrtx_arry.id)
        self.gl.glDrawArrays(self._kind, self.idx_bound.start, self.idx_bound.len)


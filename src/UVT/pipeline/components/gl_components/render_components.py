from .gl_component import OpenglComponent
from .._component import *
from ..mess_toolbox import np_gl_type_convert
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

class DrawElement(RenderComponent):
    """
    Render components of glDrawElement()
    """
    vrtx_arry = Input()
    indx_bffr = Input()
    mode = Input()
    count = Input()

    def __init__(self, window, vrtx_arry=None, indx_bffr=None, mode=None, count=None):
        super().__init__(window)
        self.vrtx_arry = vrtx_arry
        self.mode = mode
        self.count = count

    def operate(self):
        self.w.gl.glBindVertexArray(self.vrtx_arry.id)
        dtype = np_gl_type_convert(self.indx_bffr.dtype)
        self.w.gl.glDrawElement(self.mode, self.indx_bffr.len(), dtype, None)


# class DrawElemTriStrip(DrawElementComponent):
#     """
#     glDrawElement(
#     """
#     _mode = opengl.GL_TRIANGLE_STRIP
#     opengl.glDrawElements()


class DrawTriangle(DrawArrayComponent):
    """
    glDrawArrays(GL_TRIANGLES, ...)
    """

    vrtx_arry = Input(def_val=None)
    idx_bound = Input(def_val=Bound(0, 3))
    render_result = Output(None)

    _kind = opengl.GL_TRIANGLES

    def __init__(self, window=None, vao=None, idx_bound=None):
        super().__init__(window)
        self.vrtx_arry = vao
        if idx_bound is not None:
            self.idx_bound = idx_bound

    def operate(self):
        try:
            self.render()
            self.render_result = True
        except Exception as e:
            warnings.warn(e)
            self.render_result = False

    # @log_execution
    def render(self):
        self.gl.glBindVertexArray(self.vrtx_arry.id)
        self.gl.glDrawArrays(self._kind, self.idx_bound.start, self.idx_bound.len)


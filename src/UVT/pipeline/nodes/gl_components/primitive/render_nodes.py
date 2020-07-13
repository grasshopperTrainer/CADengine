from ..opengl_node import OpenglNode
from ..._node import *
from UVT.hooked import gl, glfw


class RenderComponent(OpenglNode):
    """
    Renderable nodes

    Render trigered by Window._run -> Pipeline.render -> RenderComponent.render
    """

    @property
    def is_renderable(self):
        return True

    def render(self):
        raise NotImplementedError


class DrawArrayComponent(RenderComponent):
    """
    Render nodes of glDrawArrays()
    """
    _kind = None


class RenderElement(RenderComponent):
    """
    Render nodes of glDrawElement()
    """
    in0_vrtx_arry = Input()
    in1_indx_bffr = Input()
    in2_mode = Input()

    def __init__(self, vrtx_arry=None, indx_bffr=None, mode=None):
        
        self.in0_vrtx_arry = vrtx_arry
        self.in1_indx_bffr = indx_bffr
        self.in2_mode = mode
        # self.in3_count = count

    def calculate(self):
        # try:
        gl.glBindVertexArray(self.in0_vrtx_arry.id)
        name, size, dtype, stride, offset = self.in1_indx_bffr.data.properties[0]

        gl.glDrawElements(
            self.in2_mode.r,
            size,
            dtype,
            None)
        gl.glBindVertexArray(0)






# class DrawElemTriStrip(DrawElementComponent):
#     """
#     glDrawElement(
#     """
#     _mode = opengl.GL_TRIANGLE_STRIP
#     opengl.glDrawElements()


class RenderArray(DrawArrayComponent):
    """
    glDrawArrays(GL_TRIANGLES, ...)
    """

    in0_vrtx_arry = Input(def_val=None)
    in1_prgrm = Input()
    in2_mode = Input()
    in3_idx_bound = Input(def_val=Bound(0, 3))

    def __init__(self, vrtx_arry, prgrm=None, mode=None, idx_bound=None):
        super().__init__()
        self.in0_vrtx_arry = vrtx_arry
        self.in1_prgrm = prgrm
        self.in2_mode = mode
        if idx_bound is not None:
            self.in3_idx_bound = idx_bound

    def calculate(self):
        if self.in1_prgrm.r is not None:
            gl.glUseProgram(self.in1_prgrm.r.id)
        gl.glBindVertexArray(self.in0_vrtx_arry.id)
        gl.glDrawArrays(self.in2_mode.r, self.in3_idx_bound.start, self.in3_idx_bound.len)
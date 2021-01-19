from .._opengl import *
import OpenGL.GL as gl


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


    def calculate(self, vrtx_arry, prgrm, mode, idx_bound):
        if prgrm is not None:
            gl.glUseProgram(prgrm.id)
        gl.glBindVertexArray(vrtx_arry.id)
        gl.glDrawArrays(mode, 0, 3)
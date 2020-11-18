from .window_properties import *
from .glyph_node import Glyph_node

class Views(RenderTargetPool):
    def __init__(self, window):
        super().__init__(window)
        self._append_new_target(View(0, 0, 1.0, 1.0, *window._glyph.output_intfs[:-1], self))

    def new_view(self, x_exp, y_exp, w_exp, h_exp):
        """
        Appendd new view into view pool.

        :param x_exp: expression for origin coordinate x
        :param y_exp: expression for origin coordinate y
        :param w_exp: expression for origin coordinate w
        :param h_exp: expression for origin coordinate h
        :return:
        """
        self._append_new_target(View(x_exp, y_exp, w_exp, h_exp, *self.window._glyph.output_intfs[:-1], self))


class View(RenderTarget):
    def __init__(self, x_exp, y_exp, w_exp, h_exp, par_x, par_y, par_w, par_h, pool):
        super().__init__(pool)

        self._glyph = Glyph_node(x_exp, y_exp, w_exp, h_exp, par_x, par_y, par_w, par_h)

    @property
    def glyph(self):
        return self._glyph

#
# class ViewNode(NodeBody):
#     pass
#
# @Singleton
# class GetCurrentCamera(ViewNode):
#     in0_current_camera = Input()
#
#     body_left = Output()
#     body_right = Output()
#     body_bottom = Output()
#     body_top = Output()
#     body_near = Output()
#     body_far = Output()
#     body_hfov = Output()
#     body_vfov = Output()
#     body_aspect_ratio = Output()
#     body_PM = Output()
#
#     tripod_plane = Output()
#     tripod_VM = Output()
#
#     def __init__(self):
#         super().__init__()
#         self.in0_current_camera = CameraCurrentStack().out0_current_camera
#
#     def calculate(self, cam):
#         return cam.output_values
#
#
# @Singleton
# class ViewCurrentStack(ViewNode):
#     _current_stack = []
#     out0_current_view = Output()
#
#     def __init__(self):
#         super().__init__()
#
#     def calculate(self):
#         if self._current_stack:
#             return self._current_stack[-1]
#         return None
#
#     def append(self, cam):
#         self._current_stack.append(cam)
#         self.refresh()
#
#     def pop(self):
#         self._current_stack.pop()
#         self.refresh()

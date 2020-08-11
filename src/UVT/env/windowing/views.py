from .window_properties import *
from .glyph import Glyph

class Views(RenderTargetPool):
    def __init__(self, window):
        super().__init__(window)
        self.append_new_target(View(0, 0, 1.0, 1.0, *window._glyph.output_intfs[:-1]))


class View(RenderTarget):
    def __init__(self, x_exp, y_exp, w_exp, h_exp, par_x, par_y, par_w, par_h):
        super().__init__()
        self._glyph = Glyph(x_exp, y_exp, w_exp, h_exp, par_x, par_y, par_w, par_h)
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

from .window_properties import *
from .glyph import Glyph

class Views(RenderTargetPool):
    def __init__(self, window):
        super().__init__(window)
        self.append_new_target(View(self,1.0, 1.0, window._glyph.out0_width, window._glyph.out1_height))


class View(RenderTarget, Glyph):

    def __init__(self, pool, width_exp, height_exp, parent_width, parent_height):
        super().__init__(pool, width_exp, height_exp, parent_width, parent_height)
        self._width_exp = width_exp
        self._height_exp = height_exp

    def calculate(self, w_e, h_e, p_w, p_h):
        w, h = self._calc_real_v(w_e, p_w), self._calc_real_v(h_e, p_h)
        return w, h, w/h

    def _calc_real_v(self, exp, parent_v):
        if isinstance(exp, int):
            return exp
        elif isinstance(exp, float):
            if parent_v is None:
                return 0
            else:
                return exp*parent_v
        elif callable(exp):
            if parent_v is None:
                return 0
            else:
                return exp(parent_v)

    @property
    def width_exp(self):
        return self._width_exp
    @width_exp.setter
    def width_exp(self, v):
        if not isinstance(v, (int, float)) or not callable(v):
            return TypeError('expression should be one of int, float, lambda(callable)')
        self._width_exp = v

    @property
    def height_exp(self):
        return self._height_exp
    @height_exp.setter
    def width_exp(self, v):
        if not isinstance(v, (int, float)) or not callable(v):
            return TypeError('expression should be one of int, float, lambda(callable)')
        self._height_exp = v

    @property
    def width(self):
        return self.out0_width
    @property
    def height(self):
        return self.out1_height
    @property
    def aspect_ratio(self):
        return self.out2_aspect_ratio
from noding import *


class Glyph(NodeBody):
    in0_width_exp = Input(typs=(int, float, callable))
    in1_height_exp = Input(typs=(int, float, callable))
    in2_parent_width = Input(None)
    in3_parent_height = Input(None)

    out0_width = Output()
    out1_height = Output()
    out2_aspect_ratio = Output()

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
    def width(self):
        return self.out0_width.r
    @property
    def height(self):
        return self.out1_height.r
    @property
    def aspect_ratio(self):
        return self.out2_aspect_ratio.r
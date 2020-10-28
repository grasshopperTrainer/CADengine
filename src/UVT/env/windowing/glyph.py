from JINTFP import *


class Glyph(NodeBody):
    posx_exp = Input(typs=(int, float, callable))
    posy_exp = Input(typs=(int, float, callable))
    width_exp = Input(typs=(int, float, callable))
    height_exp = Input(typs=(int, float, callable))
    parent_posx = Input()
    parent_posy = Input()
    parent_width = Input()
    parent_height = Input()

    posx = Output()
    posy = Output()
    width = Output()
    height = Output()
    aspect_ratio = Output()

    def calculate(self, xe, ye, we, he, x, y, w, h):
        results = []
        for e, p in zip((xe, ye, we, he), (x, y, w, h)):
            results.append(self._calc_real_v(e, p))
        results.append(results[2]/results[3]) # ratio
        return results

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
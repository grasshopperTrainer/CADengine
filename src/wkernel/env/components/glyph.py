import abc

from JINTFP import *
from gkernel.dtype.nongeometric.matrix import *


class GlyphInterface(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def glyph(self):
        """
        should be implemented as property
        :return: GlyphNode instance
        """
        pass


class GlyphNode(NodeBody):
    posx_exp = Input(typs=(int, float, callable))
    posy_exp = Input(typs=(int, float, callable))
    width_exp = Input(typs=(int, float, callable))
    height_exp = Input(typs=(int, float, callable))

    parent_posx = Input()
    parent_posy = Input()
    parent_width = Input()
    parent_height = Input()

    parent_trans_matrix = Input(typs=(Mat4, None), def_val=TrnsfMats())

    posx = Output()
    posy = Output()
    width = Output()
    height = Output()

    aspect_ratio = Output()
    trnsf_matrix = Output()

    def calculate(self, xe, ye, we, he, x, y, w, h, ptm):
        results = []
        for e, p in zip((xe, ye, we, he), (w, h, w, h)):
            results.append(self._calc_real_value(e, p))
        results.append(results[2] / results[3])  # ratio
        # transformation matrix
        if any([v is None for v in (x, y, w, h)]):
            results.append(ptm)
        else:
            translate_m = MoveMat(results[0] - x, results[1] - y, 0)
            scale_m = ScaleMat(results[2] / w, results[3] / h)
            matrix = ptm.copy()
            matrix.append_all(scale_m, translate_m)
            results.append(matrix)
        return results

    def _calc_real_value(self, exp, parent_v):
        if isinstance(exp, int):
            return exp
        elif isinstance(exp, float):
            if parent_v is None:
                return 0
            else:
                return int(exp * parent_v)
        elif callable(exp):
            if parent_v is None:
                return 0
            else:
                return int(exp(parent_v))

    @property
    def size(self):
        return self.width.r, self.height.r

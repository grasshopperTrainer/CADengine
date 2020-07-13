from .._node import *


class ViewNode(Node):
    
    x = Input(def_val=0.5, typs=(int, float, callable))
    y = Input(def_val=0.5, typs=(int, float, callable))
    w = Input(def_val=100, typs=(int, float, callable))
    h = Input(def_val=100, typs=(int, float, callable))

    parent_x = Input(def_val=0.5, typs=int)
    parent_y = Input(def_val=0.5, typs=int)
    parent_w = Input(def_val=100, typs=int)
    parent_h = Input(def_val=100, typs=int)

    real_x = Output(def_val=0.5, typs=int)
    real_y = Output(def_val=0.5, typs=int)
    real_w = Output(def_val=100, typs=int)
    real_h = Output(def_val=100, typs=int)

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def calculate(self):
        for n in ('x', 'y', 'w', 'h'):
            setattr(self, f"real_{n}", int(self._calc_real(n)))

    def _calc_real(self, attr_name):
        attr = getattr(self, attr_name).r

        if isinstance(attr, int):
            return attr
        elif isinstance(attr, float):
            parent_v = getattr(self, f"parent_{attr_name}").r
            if parent_v is None:
                self.__delattr__(attr_name)
                return getattr(self, attr_name)
            else:
                return attr * parent_v
        elif callable(attr):
            parent_v = getattr(self, f"parent_{attr_name}")
            if parent_v is None:
                self.__delattr__(attr_name)
                return getattr(self, attr_name)
            else:
                return attr(parent_v)
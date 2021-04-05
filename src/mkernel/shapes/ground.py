from mkernel.shapes.base import NongeoShape
from ..renderers.groudn_renderer import GroundRenderer
from gkernel.color.primitive import ClrRGBA
import OpenGL.GL as gl


class Ground(NongeoShape):
    def __init__(self, color, renderer, model):
        self.__model = model
        self.__block = renderer.vbo.cache.request_block(size=4)
        l = 1
        self.__block['pos'] = (-l, -l, 0), (l, -l, 0), (l, l, 0), (-l, l, 0)  # cover whole NDC
        self.__color = ClrRGBA(*color)
        self.__block['clr'] = self.__color

    @property
    def clr(self):
        return self.__color

    @clr.setter
    def clr(self, v):
        self.__color[:] = v
        self.__block['clr'] = v

    def delete(self):
        self.__block.release()

        self.__model.remove_shape(self)

        for k in self.__dict__.keys():
            setattr(self, k, None)
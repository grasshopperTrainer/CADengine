from mkernel.shapes.base import NongeoShape
from mkernel.global_id_provider import GIDP


class Axis(NongeoShape):
    def __init__(self, geo, renderer, model):
        self.__vrtx_block = renderer.vbo.cache.request_block(size=1)
        self.__indx_block = renderer.ibo.cache.request_block(size=1)
        self.__indx_block['idx'] = self.__vrtx_block.indices
        self.__vrtx_block['oid'] = GIDP().register_entity(self).as_rgba_float()

        self.__geo = self.geo = geo
        self.__thk = self.thk = 16  # pixel thickness

    @property
    def geo(self):
        return self.geo

    @geo.setter
    def geo(self, ray):
        self.__geo = ray
        self.__vrtx_block['ori'] = ray.origin.T
        self.__vrtx_block['dir'] = ray.as_vec().T

    @property
    def thk(self):
        return self.__thk

    @thk.setter
    def thk(self, v):
        self.__thk = v
        self.__vrtx_block['thk'] = v

    def delete(self):
        raise NotImplementedError

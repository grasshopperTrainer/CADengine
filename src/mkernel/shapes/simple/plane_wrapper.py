import gkernel.dtype.geometric.primitive as gt
from mkernel.global_id_provider import GIDP
from .base import SimpleShape


class Pln(SimpleShape):
    def __init__(self, geo, renderer, model):
        self.__vrtx_block = renderer.vbo.cache.request_block(size=1)
        self.__vrtx_block['cid'] = GIDP().register_entity(self).as_rgb_float()
        self.__indx_block = renderer.ibo.cache.request_block(size=1)
        self.__indx_block['idx'] = self.__vrtx_block.indices
        super().__init__(model, self.__vrtx_block, self.__indx_block)

        self.__geo = None
        self.__len = None

        self.geo = geo
        # think it as % of ndc
        self.len = 0.25

    @property
    def geo(self):
        return self.__geo

    @geo.setter
    def geo(self, v):
        if not isinstance(v, gt.Pln):
            raise TypeError
        if self.__geo is None:
            self.__geo = v.copy()
        self.__geo[:] = v
        v = v.T
        self.__vrtx_block['ori'] = v[0]
        self.__vrtx_block['x'] = v[1]
        self.__vrtx_block['y'] = v[2]
        self.__vrtx_block['z'] = v[3]

    @property
    def len(self):
        return self.__len

    @len.setter
    def len(self, v):
        if not isinstance(v, (int, float)):
            raise TypeError
        self.__len = v
        self.__vrtx_block['len'] = v
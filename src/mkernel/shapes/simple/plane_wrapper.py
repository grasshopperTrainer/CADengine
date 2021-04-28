import gkernel.dtype.geometric.primitive as gt
from mkernel.global_id_provider import GIDP
from ..base import GeoShape


class Pln(GeoShape):
    def __init__(self, geo, renderer):
        vb = renderer.vbo.cache.request_block(size=1)
        goid = vb['oid'] = GIDP().register_entity(self).as_rgba_float()
        ib = renderer.ibo.cache.request_block(size=1)
        ib['idx'] = vb.indices
        super().__init__(goid, (vb, ), (ib, ))

        self._geo = self.geo = geo
        # think it as % of ndc
        self.__len = self.len = 0.25

    @property
    def geo(self):
        return self._geo

    @geo.setter
    def geo(self, v):
        if not isinstance(v, gt.Pln):
            raise TypeError
        self._geo[:] = v
        v = v.T
        self.vrtx_block['ori'] = v[0]
        self.vrtx_block['x'] = v[1]
        self.vrtx_block['y'] = v[2]
        self.vrtx_block['z'] = v[3]

    @property
    def len(self):
        return self.__len

    @len.setter
    def len(self, v):
        if not isinstance(v, (int, float)):
            raise TypeError
        self.__len = v
        self.vrtx_block['len'] = v

from mkernel.shapes.base import GeoShape
from mkernel.global_id_provider import GIDP


class Axis(GeoShape):
    def __init__(self, geo, renderer):
        vb = renderer.vbo.cache.request_block(size=1)
        ib = renderer.ibo.cache.request_block(size=1)
        ib['idx'] = vb.indices
        goid = vb['oid'] = GIDP().register_entity(self).as_rgba_float()
        super().__init__(goid, (vb, ), (ib, ))

        self.geo = geo
        self._thk = self.thk = 16  # pixel thickness

    @property
    def geo(self):
        return self._geo

    @geo.setter
    def geo(self, ray):
        self._geo = ray
        self.vrtx_block['ori'] = ray.origin.T
        self.vrtx_block['dir'] = ray.as_vec().T

    @property
    def thk(self):
        return self._thk

    @thk.setter
    def thk(self, v):
        self._thk = v
        self.vrtx_block['thk'] = v

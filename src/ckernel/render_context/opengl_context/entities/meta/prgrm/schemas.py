from ckernel.render_context.opengl_context.bffr_cache import BffrCache
from ckernel.render_context.opengl_context.entities.meta.others import MetaVrtxBffr
from ckernel.render_context.opengl_context.entities.draw_bffr import DrawBffr

import numpy as np

"""
Schemas describes data structure of shader parameters
and has methods for creating buffer cache.
"""


class _GLSLParamSchema:
    @property
    def dtype(self):
        return self._dtype

    @property
    def locs(self):
        return self._locs

    def __str__(self):
        return f"<{self.__class__.__name__}: {self._dtype}>"


class VrtxAttrSchema(_GLSLParamSchema):
    """
    Vertex attribute skema
    """

    def __init__(self, dtype, locs):
        self._dtype = dtype
        self._attr_locs = locs

    def create_bffr_cache(self, size) -> BffrCache:
        """
        create buffer cache for vertex attributes

        :param size: size o
        :return:
        """
        cache = BffrCache(self._dtype, self._attr_locs, size)
        return cache

    def create_vrtx_bffr(self, attr_locs=None) -> MetaVrtxBffr:
        """
        create vertex buffer factory that describes entire vertex attribute set
        :return:
        """
        if attr_locs is None:
            dtype = self._dtype
            attr_locs = self._attr_locs
        else:
            fields = list(self._dtype.fields.items())
            new_fields = []
            for i in attr_locs:
                name = fields[i][0]
                dt = fields[i][1][0]
                new_fields.append((name, dt))
            dtype = np.dtype(new_fields)

        return MetaVrtxBffr(dtype, attr_locs)

    def union(self, other):
        """
        like set.union create new schema out of two
        :return:
        """
        new_fields = {}
        for n, l in zip(self._dtype.names, self._attr_locs):
            dt = self._dtype[n]
            new_fields[l] = (n, dt.base, dt.shape)
        for n, l in zip(other._dtype.names, other._attr_locs):
            if l in new_fields and new_fields[l] != (n, other._dtype[n].base, other._dtype[n].shape):
                raise
            else:
                dt = other._dtype[n]
                new_fields[l] = (n, dt.base, dt.shape)
        locs, dtype = zip(*sorted(new_fields.items()))
        return VrtxAttrSchema(np.dtype(list(dtype)), locs)


class UfrmSchema(_GLSLParamSchema):
    """
    Uniform skema

    """

    def __init__(self, dtype, locs, def_val):
        self._dtype = dtype
        self._locs = locs
        self._def_val = def_val

    def create_bffr_cache(self, size):
        """
        create buffer cache for uniform values

        :return:
        """
        cache = BffrCache(self._dtype, self._locs, size)
        for name, val in zip(self._dtype.fields, self._def_val):
            if val is not None:
                cache.array[name][...] = val
        return cache


class FrgmOutputSchema(_GLSLParamSchema):
    def __init__(self, dtype: np.dtype, locs: (tuple, list)):
        # useless for now
        self._dtype = dtype
        self._locs = set(locs)

    def create_draw_bffr(self):
        return DrawBffr(self._locs)
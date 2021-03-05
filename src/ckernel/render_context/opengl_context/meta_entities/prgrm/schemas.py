from ckernel.render_context.opengl_context.bffr_cache import BffrCache
from ckernel.render_context.opengl_context.meta_entities.metas import MetaVrtxBffr
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


class VrtxAttrSchema(_GLSLParamSchema):
    """
    Vertex attribute skema
    """
    def __init__(self, dtype, locs):
        self._dtype = dtype
        self._locs = locs

    def __str__(self):
        return f"<{self.__class__.__name__}: {self._dtype}>"

    def create_bffr_cache(self, size) -> BffrCache:
        """
        create buffer cache for vertex attributes

        :param size: size o
        :return:
        """
        cache = BffrCache(self._dtype, self._locs, size)
        return cache

    def create_vrtx_bffr(self) -> MetaVrtxBffr:
        """
        create vertex buffer factory that describes entire vertex attribute set
        :return:
        """
        return MetaVrtxBffr(self._dtype, self._locs)

    def union(self, other):
        """
        like set.union create new schema out of two
        :return:
        """
        new_fields = {}
        for n, l in zip(self._dtype.names, self._locs):
            dt = self._dtype[n]
            new_fields[l] = (n, dt.base, dt.shape)
        for n, l in zip(other._dtype.names, other._locs):
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

    def __str__(self):
        return f"<{self.__class__.__name__}: {self._dtype}>"

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

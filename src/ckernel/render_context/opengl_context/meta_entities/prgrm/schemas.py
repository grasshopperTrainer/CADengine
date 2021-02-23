from ckernel.render_context.opengl_context.bffr_cache import BffrCache
from ckernel.render_context.opengl_context.meta_entities.metas import MetaVrtxBffr
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
            cache.array[name][...] = val
        return cache

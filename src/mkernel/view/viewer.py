import mkernel.model.shapes as st
import mkernel.view.renderers as rend
from mkernel.model.amodel import AModel


class RendererDict(dict):
    __known_renderers = {
        st.Pnt: rend.PointRenderer,
        st.Lin: rend.LineRenderer,
        st.Tgl: rend.TriangleRenderer,
        st.Pgon: rend.PolygonRenderer,
        st.Plin: rend.PolylineRenderer,
        st.Brep: rend.BrepRenderer,
        st.Pln: rend.PlaneRenderer,
        AModel: rend.ModelRenderer}

    def __getitem__(self, item):
        if not isinstance(item, type):
            raise TypeError
        if item not in self.__class__.__known_renderers:
            raise NotImplementedError('rendering of given shape is not known')

        if item not in self:
            self[item] = self.__class__.__known_renderers[item]()
        return super().__getitem__(item)


class Viewer:
    def __init__(self, modeler):
        self.__modeler = modeler
        self.__renderers = RendererDict()

    @property
    def renderers(self):
        return self.__renderers

    def render(self):
        for renderer in self.renderers.values():
            renderer.render()

    def malloc_shape(self, shape):
        self.renderers[shape.__class__].malloc_shape(shape)

    def free_shape(self, shape):
        self.renderers[shape.__class__].free_shape(shape)

    def update_cache(self, shape, arg_name, value):
        # lazy mallocing
        self.malloc_shape(shape)
        self.renderers[shape.__class__].update_cache(shape, arg_name, value)

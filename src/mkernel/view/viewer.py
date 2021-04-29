import mkernel.model.shapes as st
import mkernel.view.sub_renderer as rend


class Viewer:
    __known_renderers = {
        st.Pnt: rend.PointRenderer,
        st.Lin: rend.LineRenderer,
        st.Tgl: rend.TriangleRenderer,
        st.Pgon: rend.PolygonRenderer,
        st.Plin: rend.PolylineRenderer,
        st.Brep: rend.BrepRenderer,
        st.Pln: rend.PlaneRenderer}

    def __init__(self, modeler):
        self.__modeler = modeler
        self.__type_rend = {}

    def render(self):
        for renderer in self.__type_rend.values():
            renderer.render()

    def __add_shape(self, shape):
        """
        renderer will ignore shape if already present
        
        :param shape:
        :return:
        """
        self.__type_rend[shape.__class__].add_shape(shape)

    def __checkinit_renderer(self, cls):
        if cls not in self.__type_rend:
            if cls not in self.__known_renderers:
                raise TypeError(f'rendering given shape {cls.__name__} not supported')
            renderer = self.__known_renderers[cls]
            self.__type_rend[cls] = renderer()
        return self.__type_rend[cls]

    def update_cache(self, shape, arg_name, value):
        cls = shape.__class__
        self.__checkinit_renderer(cls)
        self.__add_shape(shape)

        self.__type_rend[cls].update_cache(shape, arg_name, value)

from mkernel.view.viewer import Viewer
from mkernel.model import Model, AModel
import mkernel.model.shapes as st
import gkernel.dtype.geometric as gt


class AModeler:
    def __init__(self):
        """
        shape creator

        :param model:
        """
        self.__viewer = Viewer(self)

    def create_model(self, parent):
        if parent and parent.modeler is not self:
            raise ValueError('given parent is not a member ot this modeler')
        return AModel(parent, self)

    def add_shape(self, model, args, shape_type):
        """
        helper for adding geometric shapes like Point, Vector

        :param geo:
        :param shape_type:
        :param renderer_type:
        :return:
        """
        shape = shape_type(model, *args)
        model.add_child(shape)
        self.__viewer.malloc_shape(shape)
        return shape

    def remove_shape(self, shape):
        """
        signal viewer to remove shape trace

        :param shape:
        :return:
        """
        model = shape.parent
        model.remove_child(shape)
        self.__viewer.free_shape(shape)

    def update_viewer_cache(self, shape, arg_name, value):
        """
        viewer knows how to update cache

        :param shape:
        :param arg_name:
        :param value:
        :return:
        """
        self.__viewer.update_cache(shape, arg_name, value)

    def add_pnt(self, model, x, y, z) -> st.Pnt:
        """
        add point

        :param x: Number, coordinate x
        :param y: Number, coordinate y
        :param z: Number, coordinate z
        :return: Pnt shape
        """
        return self.add_shape(model, args=(gt.Pnt(x, y, z),), shape_type=st.Pnt)

    def add_lin(self, model, start, end) -> st.Lin:
        """
        add line

        :param start: (x, y, z), vertex start
        :param end: (x, y, z), vertex end
        :return: Lin shape
        """
        return self.add_shape(model, args=(gt.Lin(start, end),), shape_type=st.Lin)

    def add_tgl(self, model, v0, v1, v2) -> st.Tgl:
        """
        add triangle

        :param v0: (x, y, z), vertex 0
        :param v1: (x, y, z), vertex 1
        :param v2: (x, y, z), vertex 2
        :return:
        """
        return self.add_shape(model, args=(gt.Tgl(v0, v1, v2),), shape_type=st.Tgl)

    def add_plin(self, model, *vs) -> st.Plin:
        """
        add polyline
        :param vs:
        :return:
        """
        return self.add_shape(model, args=(gt.Plin(*vs),), shape_type=st.Plin)

    def add_pgon(self, model, *vs) -> st.Pgon:
        """
        add polygon

        :param vs: vertices
        :return:
        """
        return self.add_shape(model, args=(gt.Pgon(*vs),), shape_type=st.Pgon)

    def add_brep(self):
        """

        :return:
        """
        return self.add_shape(model, args=(gt.Brep(), self), shape_type=st.Brep)

    def add_pln(self, model, o, x, y, z):
        """

        coordinate values of:
        :param o: (x, y, z), origin
        :param x: (x, y, z), x axis
        :param y: (x, y, z), y axis
        :param z: (x, y, z), z axis
        :return:
        """
        return self.add_shape(model, args=(gt.Pln(o, x, y, z),), shape_type=st.Pln)

    def add_ground(self, model, color):
        """

        :param color: (r, g, b, a)
        :return:
        """
        return self.add_shape(model, args=(color,), shape_type=st.Ground)

    def render(self):
        self.__viewer.render()

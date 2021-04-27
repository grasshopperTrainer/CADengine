from gkernel.tools.intersector import Intersector as intx
import gkernel.dtype.geometric as gt
import mkernel.shapes as st
import mkernel.renderers as rend
from mkernel.global_id_provider import GIDP
import threading
from .base import Model


class AModel(Model):

    def add_geo_shape(self, geo):
        """
        add given geometry

        :return:
        """
        if isinstance(geo, gt.Pnt):
            return self.add_shape(args=(geo, ), shape_type=st.Pnt, renderer_type=rend.PointRenderer)
        elif isinstance(geo, gt.Lin):
            return self.add_shape(args=(geo, ), shape_type=st.Lin, renderer_type=rend.LineRenderer)
        elif isinstance(geo, gt.Tgl):
            return self.add_shape(args=(geo, ), shape_type=st.Tgl, renderer_type=rend.TriangleRenderer)
        elif isinstance(geo, gt.Pgon):
            return self.add_shape(args=(geo, ), shape_type=st.Pgon, renderer_type=rend.PolygonRenderer)
        elif isinstance(geo, gt.Plin):
            return self.add_shape(args=(geo, ), shape_type=st.Plin, renderer_type=rend.PolylineRenderer)
        elif isinstance(geo, gt.Brep):
            return self.add_shape(args=(geo, ), shape_type=st.Brep, renderer_type=rend.BrepRenderer)
        elif isinstance(geo, gt.Pln):
            return self.add_shape(args=(geo, ), shape_type=st.Pln, renderer_type=rend.PlaneRenderer)
        else:
            raise NotImplementedError

    def add_pnt(self, x, y, z) -> st.Pnt:
        """
        add point

        :param x: Number, coordinate x
        :param y: Number, coordinate y
        :param z: Number, coordinate z
        :return: Pnt shape
        """
        return self.add_shape(args=(gt.Pnt(x, y, z),), shape_type=st.Pnt, renderer_type=rend.PointRenderer)

    def add_lin(self, start, end) -> st.Lin:
        """
        add line

        :param start: (x, y, z), vertex start
        :param end: (x, y, z), vertex end
        :return: Lin shape
        """
        return self.add_shape(args=(gt.Lin(start, end),), shape_type=st.Lin, renderer_type=rend.LineRenderer)

    def add_tgl(self, v0, v1, v2) -> st.Tgl:
        """
        add triangle

        :param v0: (x, y, z), vertex 0
        :param v1: (x, y, z), vertex 1
        :param v2: (x, y, z), vertex 2
        :return:
        """
        return self.add_shape(args=(gt.Tgl(v0, v1, v2),), shape_type=st.Tgl, renderer_type=rend.TriangleRenderer)

    def add_plin(self, *vs) -> st.Plin:
        """
        add polyline
        :param vs:
        :return:
        """
        return self.add_shape(args=(gt.Plin(*vs),), shape_type=st.Plin, renderer_type=rend.PolylineRenderer)

    def add_pgon(self, *vs) -> st.Pgon:
        """
        add polygon

        :param vs: vertices
        :return:
        """
        return self.add_shape(args=(gt.Pgon(*vs),), shape_type=st.Pgon, renderer_type=rend.PolygonRenderer)

    def add_brep(self):
        """

        :return:
        """
        return self.add_shape(args=(gt.Brep(),), shape_type=st.Brep, renderer_type=rend.BrepRenderer)

    def add_pln(self, o, x, y, z):
        """

        coordinate values of:
        :param o: (x, y, z), origin
        :param x: (x, y, z), x axis
        :param y: (x, y, z), y axis
        :param z: (x, y, z), z axis
        :return:
        """
        return self.add_shape(args=(gt.Pln(o, x, y, z),), shape_type=st.Pln, renderer_type=rend.PlaneRenderer)

    def add_ground(self, color):
        """

        :param color: (r, g, b, a)
        :return:
        """
        return self.add_shape(args=(color,), shape_type=st.Ground, renderer_type=rend.GroundRenderer)

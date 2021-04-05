import gkernel.dtype.geometric as gt
from global_tools.red_black_tree import RedBlackTree
from .geometry import Geometries
from .topology import *


class InitiationError(Exception):
    def __str__(self):
        return f"already initated"


class Brep:
    def __init__(self):
        self.__topo = Topology(self)
        self.__geom = Geometries(self)

    def __str__(self):
        return f"<Brep {len(self.__geom)}>"

    @property
    def topology(self):
        return self.__topo

    @property
    def geometry(self):
        return self.__geom

    @classmethod
    def from_empty(cls):
        raise NotImplementedError

    @classmethod
    def from_lin(cls, s, e):
        """
        initiate brep from line

        1. record given line
        :param s : (x, y, z) tuple, starting coordinate
        :param e : (x, y, z) tuple, ending coordinate
        :return:
        """
        self = Brep()
        # brep is empty
        curve = gt.Lin(s, e)
        curve, s, e = self.geometry.addnew_curve(curve)
        self.topology.addnew_edge(curve, s, e)
        return self

    def add_vrtx(self, pnt):
        """
        add new vertex

        what if point already exists?
        :param pnt:
        :return: (vertex, point)
        """
        p = self.geometry.add_point(pnt)
        vrtx = self.topology.add_vrtx(p)
        return vrtx

    @classmethod
    def from_pnt(cls, x, y, z):
        # self = Brep()
        # point = gt.Pnt(x, y, z)
        # point = self.geometry.add_point(point)
        # vertex = self.topology.add_vertex(point)
        # return self
        raise NotImplementedError

    @classmethod
    def from_pgon(cls):
        raise NotImplementedError

    @classmethod
    def from_primitive(cls, primitive):
        raise NotImplementedError

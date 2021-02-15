import gkernel.dtype.geometric as gt
from global_tools.red_black_tree import RedBlackTree


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

    def addget_vrtx(self, x, y, z):
        """
        add new vertex

        what if point already exists?
        :param pnt:
        :return: (vertex, point)
        """
        pnt = gt.Pnt(x, y, z)
        if self.geometry.is_unique_point(pnt):
            p = self.geometry.add_point(pnt)
            v = self.topology.add_vertex(p)
        else:
            p = self.geometry.get_coincident_point(pnt)
            v = self.topology.get_coincident_vertex(pnt)
        return v, p

    def iter_edges(self):
        pass

    @classmethod
    def from_pnt(cls, x, y, z):
        self = Brep()
        point = gt.Pnt(x, y, z)
        point = self.geometry.add_point(point)
        vertex = self.topology.add_vertex(point)
        return self

    @classmethod
    def from_pgon(cls):
        raise NotImplementedError

    @classmethod
    def from_primitive(cls, primitive):
        raise NotImplementedError


class Topology:
    def __init__(self, brep):
        self.__brep = brep

        self.__vertices = []
        self.__edges = []
        self.__faces = []

    @property
    def edges(self):
        return tuple(self.__edges)

    @property
    def vertices(self):
        return self.__vertices

    def add_vertex(self, pnt):
        vrtx = Vertex(pnt)
        self.__vertices.append(vrtx)
        return vrtx

    def addnew_edge(self, curve, start, end):
        """
        add new edge

        :param curve:
        :return:
        """
        edge = Edge(curve, start, end)
        self.__edges.append(edge)
        vs, ve = Vertex(start), Vertex(end)
        vs.append_edge(edge)
        ve.append_edge(edge)
        self.__vertices.append(vs)
        self.__vertices.append(ve)
        return edge

    def get_coincident_vertex(self, pnt):
        for v in self.__vertices:
            if v.point == pnt:
                return v
        return None


class Edge:
    def __init__(self, curve, start, end):
        self.__curve = curve
        self.__half_edges = HalfEdge(self, 0, start), HalfEdge(self, 1, end)

    def __str__(self):
        return f"<Edge {self.__curve}>"

    def __repr__(self):
        return self.__str__()

    @property
    def half_edges(self):
        return self.__half_edges


class HalfEdge:
    def __init__(self, edge, index, term):
        self.__edge = edge

        self.__idx = index
        self.__next = None
        self.__term = term
        self.__face = None

    def __str__(self):
        return f"<HalfEdge {self.__idx}>"

    def __repr__(self):
        return self.__str__()


class Vertex:
    def __init__(self, point):
        self.__point = point
        self.__edges = []

    def __str__(self):
        return f"<Vertex {self.__point}>"

    def __repr__(self):
        return self.__str__()

    @property
    def point(self):
        return self.__point

    def append_edge(self, edge):
        self.__edges.append(edge)

# class Shell:
#     """
#     Separate space
#     """
#     def __init__(self):
#         pass


class Geometries:
    def __init__(self, brep):
        self.__brep = brep
        self.__surface = {}
        self.__curve = {}
        self.__point = {}

    def __str__(self):
        return f"<BrepGeometry s:{self.num_surfaces} c:{self.num_curves} p:{self.num_points}>"

    def __len__(self):
        return self.num_surfaces + self.num_curves + self.num_points

    @property
    def num_surfaces(self):
        return sum([len(v) for v in self.__surface.values()])

    @property
    def num_curves(self):
        return sum([len(v) for v in self.__curve.values()])

    @property
    def num_points(self):
        return sum(len(v) for v in self.__point.values())

    def iter_points(self):
        for vs in self.__point.values():
            for v in vs:
                yield v

    def iter_curves(self):
        raise NotImplementedError

    def iter_surfaces(self):
        raise NotImplementedError

    def is_unique_point(self, pnt):
        """
        check if point is unique

        :param pnt:
        :return:
        """
        if pnt.__class__ not in self.__point:
            return True
        else:   # checking red black tree
            return not self.__point[__class__].has_value(pnt)

    def add_point(self, pnt):
        """
        register point
        :return:
        """
        if not self.is_unique_point(pnt):
            raise Exception('coincident point')
        self.__point.setdefault(pnt.__class__, RedBlackTree()).insert(pnt)
        return pnt

    def addnew_curve(self, curve):
        """
        register curve and return curve, start-end points

        :param curve:
        :return: curve, start point, end point
        """
        start, end = curve.start, curve.end

        # 0. check existence
        pcurve = self.get_coincident_curve(curve)
        pstart = self.get_coincident_curve(start)
        pend = self.get_coincident_curve(end)
        if all([g is not None for g in (pcurve, pstart, pend)]):
            raise Exception('trying to register pre-existing curve')

        # 1. check coincident edge
        if not pcurve:
            self.__curve.setdefault(curve.__class__, []).append(curve)
            pcurve = curve
        # 2. check coincident points
        if not pstart:
            self.__point.setdefault(start.__class__, RedBlackTree()).insert(start)
            pstart = start
        if not pend:
            self.__point.setdefault(start.__class__, RedBlackTree()).insert(end)
            pend = end

        return pcurve, pstart, pend

    def __getadd_curve(self, curve):
        """
        check existence of a curve
        and add, return given curve if absent,
        else return pre-existing

        :return:
        """
        present = self.get_coincident_curve(curve)
        if present:
            return present
        else:
            self.__curve.setdefault(curve.__class__, []).append(curve)
            return curve

    def __getadd_point(self, point):
        """
        check existence of a curve
        and add, return given curve if absent,
        else return pre-existing

        :param point:
        :return:
        """
        present = self.get_coincident_point(point)
        if present:
            return present
        else:
            self.__point.setdefault(point.__class__, RedBlackTree()).insert(point)
            return point

    def get_coincident_curve(self, curve):
        """
        check if curve pre exists

        :param curve:
        :return:
        """
        # if no record of its kind
        if curve.__class__ not in self.__curve:
            return None
        # if using RBtree, objects has to have ==, <
        # but is it logical for geometry have such operations?
        # line can be sorted but curves cant
        # what data structure can be used to speed up searching?
        for obj in self.__curve[curve.__class__]:
            if obj == curve:
                return obj
        return None

    def get_coincident_point(self, point):
        if point.__class__ not in self.__point:
            return None

        for obj in self.__point.get(point.__class__, []):
            if obj == point:
                return point
        return None



import gkernel.dtype.geometric as gt


class Topology:
    """
    stores geometry and relationship in between geometries
    """
    def __init__(self):

        self.__vertices = []
        self.__edges = []
        self.__faces = []

    @property
    def edges(self):
        return tuple(self.__edges)

    @property
    def vertices(self):
        return self.__vertices

    def add_vrtx(self, pnt):
        vrtx = Vertex(pnt)
        self.__vertices.append(vrtx)
        return vrtx

    def define_line_edge(self, svrtx, evrtx):
        """
        define edge between two vertices

        :param svrtx:
        :param evrtx:
        :return:
        """
        curve = gt.Lin.from_pnts(svrtx.geo, evrtx.geo)
        edge = Edge(curve, svrtx, evrtx)
        return edge

    #
    # def addnew_edge(self, curve, start, end):
    #     """
    #     add new edge
    #
    #     :param curve:
    #     :return:
    #     """
    #     edge = Edge(curve, start, end)
    #     self.__edges.append(edge)
    #     vs, ve = Vertex(start), Vertex(end)
    #     vs.append_edge(edge)
    #     ve.append_edge(edge)
    #     self.__vertices.append(vs)
    #     self.__vertices.append(ve)
    #     return edge
    #
    # def get_coinoident_vertex(self, pnt):
    #     for v in self.__vertices:
    #         if v.point == pnt:
    #             return v
    #     return None


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

    @property
    def geo(self):
        return self.__curve


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
    def geo(self):
        return self.__point

    def append_edge(self, edge):
        self.__edges.append(edge)

    def extrude(self, vec):
        raise NotImplementedError


# class Shell:
#     """
#     Separate space
#     """
#     def __init__(self):
#         pass


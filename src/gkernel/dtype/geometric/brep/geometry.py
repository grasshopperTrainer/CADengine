from global_tools.red_black_tree import RedBlackTree
import gkernel.dtype.geometric.primitive as pgt


class Geometries:
    """
    stores geometric entities
    Think this as mere database

    """
    def __init__(self, brep):
        self.__brep = brep
        self.__surface = {}
        self.__curve = {}
        self.__point = {}

    def __str__(self):
        return f"<BrepGeometry s:{self.num_surfaces} c:{self.num_curves} p:{self.num_points}>"

    def __len__(self):
        return self.num_surfaces + self.num_curves + self.num_points

    def is_unique(self, geo):
        if isinstance(geo, pgt.Pnt):
            return self.is_unique_point(geo)
        else:
            raise NotImplementedError

    def is_unique_point(self, pnt):
        """
        check if point is unique

        :param pnt:
        :return:
        """
        if pnt.__class__ not in self.__point:
            return True
        else:  # checking red black tree
            return not self.__point[pnt.__class__].has_value(pnt)

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

    def add_point(self, pnt):
        """
        register point
        :return:
        """
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



import gkernel.dtype.geometric as gt
from .axis_renderer import AxisRenderer
from .axis import Axis
from gkernel.color import ClrRGBA
from mkernel.global_id_provider import GIDP


class AxisPicker:
    """
    sketchup style axis picker
    """

    def __init__(self, model, id_picker, coord_picker, cursor):
        self.__model = model

        self.__id_picker = id_picker
        self.__coord_picker = coord_picker
        self.__cursor = cursor

        self.__axes = []

    def __getitem__(self, item):
        return self.__axes.__getitem__(item)

    def __iter__(self):
        return iter(self.__axes)

    def append_axis(self, ray: gt.Ray):
        self.__axes.append(self.__model.__add_shape(args=(ray,),
                                                    shape_type=Axis,
                                                    renderer_type=AxisRenderer))

    def pick_threshold(self):
        """
        pick using texture pixel picking
        :return: picked, is picked an axis, closest point on the axis
        """
        # pick goid
        goid = self.__id_picker.pick(pos=self.__cursor.pos_local, size=(1, 1))[0][0]
        goid = ClrRGBA(*goid).as_ubyte()[:3]
        entity = GIDP().get_registered(goid)
        idx = None
        for i, axis in enumerate(self.__axes):
            if entity == axis:
                idx = i
                break

        coord = self.__coord_picker.pick(self.__cursor.pos_global.astype(int), size=(1, 1))[0][0]

        return idx, gt.Pnt(*coord[:3])

    def pick_closest(self, pick_ray: gt.Ray):
        """
        pick closest axis
        :return:
        """
        distances = []
        for idx, axis in enumerate(self.__axes):

            ao = axis.geo.origin
            av = axis.geo.as_vec()
            ro = pick_ray.origin
            rv = pick_ray.as_vec()

            cv = pick_ray.origin - ao
            v0 = gt.Vec.cross(av, rv)
            v1 = gt.Vec.cross(cv, rv)
            # intersection points
            t = gt.Vec.dot(v1, v0) / (v0.length ** 2)
            p0 = ao + av * t
            s = gt.Vec.dot(rv, p0 - ro) / (rv.length ** 2)
            p1 = ro + rv * s

            distances.append(((p0 - p1).length, idx, p0))
        distances.sort()
        return distances[0][1:]

    def is_axis(self, entity):
        return entity in self.__axes

    def delete(self):
        for axis in self.__axes:
            self.__model.remove_shape(axis)
        self.__axes.clear()
        self.__model = None

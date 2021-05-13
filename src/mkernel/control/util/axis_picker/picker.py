import gkernel.dtype.geometric as gt
from .axis_renderer import AxisRenderer
from .axis import Axis
from gkernel.color import ClrRGBA
from mkernel.global_id_provider import GIDP


class AxisPicker:
    """
    sketchup style axis picker
    """

    def __init__(self, modeler, model, id_picker, coord_picker, camera, cursor):
        self.__modeler = modeler
        self.__model = model

        self.__id_picker = id_picker
        self.__coord_picker = coord_picker
        self.__camera = camera
        self.__cursor = cursor

        self.__axes = []

    def __getitem__(self, item):
        return self.__axes.__getitem__(item)

    def __iter__(self):
        return iter(self.__axes)

    def append_axis(self, ray: gt.Ray):
        """
        add axis shape to the model

        :param ray:
        :return:
        """
        if not self.__modeler.is_shape_known(Axis):
            self.__modeler.register_renderer(Axis, AxisRenderer)

        axis = self.__modeler._add_shape(parent=None,
                                         args=(ray,),
                                         shape_type=Axis)
        self.__axes.append(axis)

    def pick_threshold(self):
        """
        Pick adequate axis if distance between frustum ray and axis is under threshold.

        pick using texture pixel picking
        :return: picked, is picked an axis, closest point on the axis
        """
        # pick goid
        goid, bitpattern = self.__id_picker.pick(pos=self.__cursor.pos_local, size=(1, 1))
        entity = GIDP().get_registered_byvalue(goid[0][0], bitpattern)

        # if picking axis
        for i, axis in enumerate(self.__axes):
            if entity == axis:
                # pick closest point on axis
                coord = self.__coord_picker.pick(self.__cursor.pos_local, size=(1, 1))[0][0][0]
                return i, gt.Pnt(*coord[:3])
        return None, None

    def pick_closest(self):
        """
        pick closest axis
        :return:
        """
        ray = self.__camera.frusrum_ray(*self.__cursor.pos_local.xy)

        distances = []
        for idx, axis in enumerate(self.__axes):
            ao = axis.geo.origin
            av = axis.geo.as_vec()
            ro = ray.origin
            rv = ray.as_vec()

            cv = ray.origin - ao
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

    def release_axes(self):
        """

        :return:
        """
        for axis in self.__axes:
            self.__modeler.remove_shape(axis)
        self.__axes.clear()

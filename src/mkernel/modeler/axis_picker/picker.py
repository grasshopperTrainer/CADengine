import gkernel.dtype.geometric as gt
from .axis_renderer import AxisRenderer
from .axis import Axis


class AxisPicker:
    """
    sketchup style axis picker
    """

    def __init__(self, model):
        self.__model = model
        self.__axes = []

    def __getitem__(self, item):
        return self.__axes.__getitem__(item)

    def append_axis(self, ray: gt.Ray):
        self.__axes.append(self.__model.add_shape(args=(ray,),
                                                  shape_type=Axis,
                                                  renderer_type=AxisRenderer))

    def is_axis(self, entity):
        return entity in self.__axes

    def closest_pnt(self):
        print('ddd')

    def remove_all(self):
        raise NotImplementedError
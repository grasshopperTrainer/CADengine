from .._component import *
from .gl_component import OpenglComponent


class ConDataComponent(OpenglComponent):
    """
    Parent for data components using numpy array
    """
    val_out = Output(None)

    def __init__(self, data):
        if isinstance(data, (tuple, list)):
            self.val_out = FloatVector(np.array(data, dtype=self._dtype))
        elif isinstance(data, np.array):
            self.val_out = FloatVector(data)
        else:
            raise NotImplementedError

    @property
    def is_renderable(self):
        return False


class ConFloatVector(ConDataComponent):
    _dtype = 'f'


class ConUnsignedIntVector(ConDataComponent):
    _dtype = 'uint'


class Window(OpenglComponent):
    window = Output(None)

    def __init__(self, w):
        self.window = w
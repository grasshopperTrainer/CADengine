from mkernel.shapes.base import Shape
from mkernel.global_id_provider import GIDP


class SimpleShape(Shape):
    """
    Those using single vertex block and single index block
    """

    def __init__(self, model, vrtx_block, indx_block):
        self._model = model
        self._vrtx_block = vrtx_block
        self._indx_block = indx_block

    def delete(self):
        arr = self._indx_block.arr
        self._vrtx_block.release()
        self._indx_block.release()

        GIDP().deregister(self)
        self._model.remove_shape(self)

        for k, v in self.__dict__.items():
            setattr(self, k, None)

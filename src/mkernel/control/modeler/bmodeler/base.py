from mkernel.control.modeler import AModeler
from mkernel.model import BModel
# from mkernel.model.shapes import Brep
# from mkernel.control.util.vicinity_picker import VicinityPicker


class BModeler(AModeler):
    def __init__(self):
        super(BModeler, self).__init__()

    def add_model(self, parent):
        return self._add_shape(parent, (self, ), BModel)
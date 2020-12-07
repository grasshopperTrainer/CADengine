from ..dtype import *
from JINTFP import *

class GeomKernelNode(NodeBody):
    pass

class DataContainer(GeomKernelNode):
    in0_data = Input()
    out0_data = Output()

class PlaneContainer(DataContainer):

    def __init__(self, plane=None):
        if plane is None:
            plane = Pln()
        super().__init__(plane)

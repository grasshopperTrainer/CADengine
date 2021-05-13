from mkernel.model.amodel import AModel
from .topology import Topology


class BModel(AModel):
    """
    this is a V from MVC
    is this BREP itself?
    """
    def __init__(self, modeler):
        super(BModel, self).__init__(modeler)
        self.__topology = Topology()

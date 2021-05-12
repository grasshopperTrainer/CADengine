from mkernel.control.modeler.base import Modeler
from mkernel.model.shapes import Brep
from mkernel.control.util.vicinity_picker import VicinityPicker


class BModeler(Modeler):
    def __init__(self, root_brep: Brep):
        super().__init__()
        self.__curr_brep = root_brep
        self.__last_button_stat = {i: 0 for i in range(3)}

        self.__frame_bffr = None
        self.__vp = VicinityPicker(offset=500)

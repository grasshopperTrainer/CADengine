import weakref
from .base import Modeler
from .vicinity_picker import VicinityPicker
from ..global_id_provider import GIDP
from gkernel.color import ClrRGBA
import mkernel.shapes as shp


class AModeler(Modeler):
    """
    Default, engine-embedded modeler
    """

    def __init__(self):
        super().__init__()
        self.__vp = VicinityPicker(offset=500)
        self.__last_button_status = {0: 0, 1: 0, 2: 0}

        self.__selected = None
        self.__selection_color = 1, 1, 0, 1

    def listen(self, model, window, mouse, keyboard, camera, cursor, id_picker):
        """
        check condition and trigger commands

        :param window:
        :param model:
        :param spp:
        :return:
        """
        # for left button press
        if mouse.get_button_status(0) and self.__last_button_status[0] != 1:
            self.execute(self.point_add_select, model, args=(window, camera, cursor, id_picker))
        elif keyboard.get_key_status('v'):
            self.execute(self.point_delete, model, args=(window, camera, cursor, id_picker))
        self.__last_button_status[0] = mouse.get_button_status(0)

    def point_add_select(self, window, camera, cursor, id_picker, model):
        """
        add new or select existing

        :param camera:
        :param cursor:
        :param id_picker: FramePixelPicker,
        :param model:
        :return:
        """
        # if selecting existing
        with window.context.gl:
            oid = id_picker.pick(cursor.pos_local, size=(1, 1))[0][0]
        clr = ClrRGBA(*oid).as_ubyte()[:3]
        shape = GIDP().get_registered(clr)

        if not shape:
            pos = self.__vp.pick(camera, cursor)[1]
            model.add_geo_shape(pos)
            if self.__selected:
                self.__remove_selected()
        else:
            if isinstance(shape, shp.Pnt):
                if self.__selected:
                    if self.__selected[0]() != shape:
                        self.__remove_selected()
                        self.__set_selected(shape)
                else:
                    self.__set_selected(shape)

    def point_delete(self, window, camera, cursor, id_picker, model):
        """

        :param window:
        :param camera:
        :param cursor:
        :param id_picker:
        :param model:
        :return:
        """
        if self.__selected:
            if self.__selected[0]() is not None:
                self.__selected[0]().delete()
        self.__selected = None

    def __remove_selected(self):
        """
        remove selected

        :return:
        """
        if self.__selected[0]() is not None:
            self.__selected[0]().clr = self.__selected[1]
        self.__selected = None

    def __set_selected(self, geo):
        """
        cache geometry as selected
        :return:
        """
        self.__selected = weakref.ref(geo), geo.clr.copy()
        geo.clr = (1, 1, 0, 1)

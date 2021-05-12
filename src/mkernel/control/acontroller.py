from mkernel.global_id_provider import GIDP
from mkernel.control.util.executor import Executor
from .util import VicinityPicker
import gkernel.dtype.geometric as gt


class AController:
    """
    basic testing controller
    """

    def __init__(self, window, modeler, model, id_picker, coord_picker, camera, cursor):
        """
        :param window: interaction has to happen to a certain window
        :param modeler: modeler that contains manipulating functions
        :param model: model to manipulate
        :param id_picker: id texture pixel picker
        :param coord_picker: coord texture pixel picker
        :param camera: interacting camera
        :param cursor: interacting cursor
        """
        self.__window = window
        self.__modeler = modeler
        self.__model = model

        self.__executor = Executor()
        self.__last_button_stat = {i: 0 for i in range(3)}
        self.__vp = VicinityPicker()
        self.__id_picker = id_picker
        self.__coord_picker = coord_picker
        self.__camera = camera
        self.__cursor = cursor

        self.__window.devices.mouse.append_mouse_button_callback(self.__callback_mouse)
        self.__window.devices.keyboard.append_key_callback(self.__callback_keyboard)

        self.__selection = None

    def __callback_mouse(self, surface, button, action, mods, mouse):
        """
        respond to mouse button action
        :return:
        """
        # basic sticky button
        if button == 0 and self.__last_button_stat[button] == 0:
            if not self.__executor.active_exec_count:
                self.__executor.execute(command=self.__left_button_press)
        self.__last_button_stat[button] = action

    def __callback_keyboard(self, surface, key, scancode, action, mods, keyboard):
        """
        respont to keyboard press

        :param surface:
        :param key:
        :param scancode:
        :param action:
        :param mods:
        :param keyboard:
        :return:
        """
        if self.__selection and keyboard.get_char(key, mods) == 'd' and action == 1:
            self.__executor.execute(self.__remove_point)

    def __left_button_press(self):
        """
        actions for left button press
        :return:
        """
        # clear selection
        if self.__selection:
            self.__selection.clr = 1, 1, 1, 1
            self.__selection = None

        # check for selection
        # as this is a separate thread, need context binding
        with self.__window.context.gl:
            goid, bitpatt = self.__id_picker.pick(pos=self.__cursor.pos_local, size=(1, 1))
        shape = GIDP().get_registered_byvalue(goid[0][0], bitpatt)

        # if nothing selected,
        if shape is None:
            pick = self.__vp.pick(gt.Pln(), self.__camera, self.__cursor)
            if pick:
                self.__executor.execute(self.__draw_point, args=(pick[1],))
        else:  # picking drawn point
            self.__executor.execute(self.__color_selected, args=(shape,))

    def __draw_point(self, pnt):
        self.__modeler.add_raw(self.__model, pnt)

    def __color_selected(self, pnt):
        self.__selection = pnt
        pnt.clr = 1, 1, 0, 1

    def __remove_point(self):
        self.__modeler.remove_shape(self.__selection)
        self.__selection = None

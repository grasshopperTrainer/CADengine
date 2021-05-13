import gkernel.dtype.geometric as gt
from mkernel.global_id_provider import GIDP

from .util.executor import Executor
from .util.vicinity_picker import VicinityPicker
from .util.axis_picker import AxisPicker


class JController:

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

        self.__window.devices.mouse.append_mouse_button_callback(self.__callback_mouse_button)
        self.__window.devices.mouse.append_cursor_pos_callback(self.__callback_cursor_pos)
        self.__window.devices.keyboard.append_key_callback(self.__callback_keyboard)

        self.__guide_Line = None
        self.__ap = AxisPicker(self.__modeler,
                               self.__model,
                               self.__id_picker,
                               self.__coord_picker,
                               self.__camera,
                               self.__cursor)

    def __callback_mouse_button(self, surface, button, action, mods, mouse):
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
        if self.__guide_Line and keyboard.get_char(key, mods) == 'd' and action == 1:
            self.__executor.execute(self.__remove_point)

    def __callback_cursor_pos(self, surface, xpos, ypos, mouse):
        if self.__ap and self.__guide_Line is not None:
            self.__update_guideline()

    def __left_button_press(self):
        """
        actions for left button press
        :return:
        """
        # check for selection
        # as this is a separate thread, need context binding
        with self.__window.context.gl:
            goid, bitpatt = self.__id_picker.pick(pos=self.__cursor.pos_local, size=(1, 1))
        shape = GIDP().get_registered_byvalue(goid[0][0], bitpatt)

        # if nothing selected
        if shape is None:
            # if not in draw state
            if self.__guide_Line is None:
                idx, pnt = self.__vp.pick(gt.Pln(), self.__camera, self.__cursor)
                if pnt is not None:
                    self.__executor.execute(self.__start_guideline, args=(pnt,))
                return
        # if in draw state, simple release line from control
        self.__executor.execute(self.__end_guideline)

    def __start_guideline(self, pnt):
        """
        set starting vertex and make invisible

        :param pnt:
        :return:
        """
        # create guild line and make unpickable
        lin = self.__modeler.add_raw(self.__model, gt.Lin.from_pnts(pnt, pnt))
        lin.goid_flag = False
        self.__guide_Line = lin

        # create axis picker based on starting vertex
        axes = self.__model.plane.axes
        for axis in axes:
            ray = gt.Ray.from_pnt_vec(origin=pnt, normal=axis)
            self.__ap.append_axis(ray)

    def __end_guideline(self):
        self.__guide_Line.clr = 1, 1, 1, 1
        self.__guide_Line = None
        self.__ap.release_axes()

    __xyz_colors = (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)

    def __update_guideline(self):
        # try snap axis and if not, pick vicinity
        with self.__window.context.gl:
            if self.__window.devices.keyboard.get_key_status('lshift'):
                idx, end_vrtx = self.__ap.pick_closest()
            else:
                idx, end_vrtx = self.__ap.pick_threshold()

        if end_vrtx is not None:
            clr = self.__xyz_colors[idx]
        else:
            idx, end_vrtx = self.__vp.pick(gt.Pln(), self.__camera, self.__cursor)
            clr = 1, 1, 1, 1

        # __end_guideline can come first
        if self.__guide_Line:
            # update guide line
            self.__guide_Line.geo = gt.Lin.from_pnts(self.__guide_Line.geo.start, end_vrtx)
            self.__guide_Line.clr = clr

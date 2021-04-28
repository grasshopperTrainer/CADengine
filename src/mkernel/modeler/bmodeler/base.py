from mkernel.modeler.base import Modeler
from gkernel.color import ClrRGBA
from mkernel.global_id_provider import GIDP
from mkernel.shapes.brep_wrapper import Brep
from mkernel.modeler.vicinity_picker import VicinityPicker
from mkernel.modeler.axis_picker.picker import AxisPicker

import gkernel.dtype.geometric as gt
from global_tools import FPSTimer


class BModeler(Modeler):
    def __init__(self, root_brep: Brep):
        super().__init__()
        self.__curr_brep = root_brep
        self.__last_button_stat = {i: 0 for i in range(3)}

        self.__frame_bffr = None
        self.__vp = VicinityPicker(offset=500)
        self.__ap = None

    def __checkinit_pickers(self, model):
        """
        lazy initiation for axis picker

        :param model:
        :return:
        """
        if not self.__ap:
            self.__ap = AxisPicker(model)

    def listen(self, model, window, mouse, camera, cursor, id_picker):
        """
        listen each frame and activate draw logics
        :return:
        """
        self.__checkinit_pickers(model)

        left_button = mouse.get_button_status(0)
        if not self.active_exec_count and left_button == 1 and self.__last_button_stat[0] == 0:
            self.execute(command=self.__left_button_press,
                         model=model,
                         args=(window, camera, cursor, id_picker),
                         block_exec=True)
        self.__last_button_stat[0] = left_button

    def __left_button_press(self, window, camera, cursor, id_picker, model):
        """
        actions for left button press
        :return:
        """
        # check for selection
        # as this is a separate thread, need context binding
        with window.context.gl:
            oid = id_picker.pick(pos=cursor.pos_local, size=(1, 1))[0][0]
        oid = ClrRGBA(*oid).as_ubyte()[:3]
        shape = GIDP().get_registered(oid)

        if shape is None:
            # start drawing line
            pnt = self.__vp.pick(camera, cursor)[1]
            if self.__curr_brep.geo.geometry.is_unique(pnt):
                vrtx = self.__curr_brep.geo.add_vrtx(pnt)
                pnt = self.__curr_brep.add_vrtx(vrtx)
                pnt.dia = 0

                self.execute(self.__draw_drawing_line, model, args=(window, vrtx, camera, cursor, id_picker))
            else:
                print('ddd')

        else:
            print('selected')

    def __draw_drawing_line(self, window, svrtx, camera, cursor, id_picker, model):
        # temporary drawing line
        xyz = svrtx.geo.xyz
        tline = model.add_lin(xyz, xyz)
        tline.do_render_id = False

        # draw snapping axis
        ap = AxisPicker(model)
        axes = model.plane.axes
        for axis in axes:
            ap.append_axis(gt.Ray.from_pnt_vec(origin=svrtx.geo, normal=axis))

        timer = FPSTimer(target_fps=window.fps)
        while True:
            with timer:

                # check for axis snap
                with window.context.gl:
                    oid = id_picker.pick(pos=cursor.pos_local, size=(1, 1))[0][0]
                    oid = ClrRGBA(*oid).as_ubyte()[:3]
                    axis = GIDP().get_registered(oid)
                # snap on to the axis
                if ap.is_axis(axis):
                    tend = ap.closest_pnt()
                else:   # pick vicinity
                    tend = self.__vp.pick(camera, cursor)[1]
                    tline.clr = 1, 1, 1, 1
                    tline.geo = gt.Lin.from_pnts(tline.geo.start, tend)

                left_pressed = False
                if window.devices.mouse.get_button_status(0) == 1 and self.__last_button_stat[0] == 0:
                    left_pressed = True

                # when left button pressed
                if left_pressed:
                    # check if any selected
                    with window.context.gl:
                        oid = id_picker.pick(pos=cursor.pos_local, size=(1, 1))[0][0]
                    oid = ClrRGBA(*oid).as_ubyte()[:3]
                    shape = GIDP().get_registered(oid)

                    # when nothing selected
                    # create new edge
                    if shape is None:
                        evrtx = self.__curr_brep.geo.add_vrtx(tend)
                        line = self.__curr_brep.geo.topology.define_line_edge(svrtx, evrtx)
                        shape = model.add_geo_shape(line.geo)
                        shape.thk = 0.5
                        shape.clr = 1, 1, 1, 1

                        tline.delete()
                        break

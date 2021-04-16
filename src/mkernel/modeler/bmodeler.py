from .base import Modeler
from gkernel.color import ClrRGBA
from mkernel.global_id_provider import GIDP
from mkernel.shapes.brep_wrapper import Brep
from .vicinity_picker import VicinityPicker
from .axis_picker import AxisPicker

import gkernel.dtype.geometric as gt
from global_tools import FPSTimer
from gkernel.tools.intersector import Intersector


class Repeater:
    def __init__(self, fps):
        self.__trgt_fps = fps


class BModeler(Modeler):
    def __init__(self, root_brep: Brep):
        super().__init__()
        self.__curr_brep = root_brep
        self.__last_button_stat = {i: 0 for i in range(3)}
        self.__vp = VicinityPicker(offset=500)
        self.__ap = AxisPicker()

    def listen(self, model, window, mouse, camera, cursor, id_picker):
        """
        listen each frame and activate draw logics
        :return:
        """
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

        timer = FPSTimer(target_fps=window.fps)
        while True:
            with timer:
                # render drawing line
                cray = camera.frusrum_ray(*cursor.pos_local.xy)
                pln = gt.Pln.from_ori_axies(svrtx.geo, *model.plane.axes)
                dist, pnt, sign = self.__ap.pick(cray, pln)
                if dist < 2:
                    tend = pnt
                    tline.clr = {'x': (1, 0, 0, 1), 'y': (0, 1, 0, 1), 'z': (0, 0, 1, 1)}[sign]
                else:
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
                        shape = model.add_geo(line.geo)
                        shape.thk = 0.5
                        shape.clr = 1, 1, 1, 1

                        tline.delete()
                        break

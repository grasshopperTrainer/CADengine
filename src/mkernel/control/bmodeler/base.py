from mkernel.control.base import Modeler
from gkernel.color import ClrRGBA
from mkernel.global_id_provider import GIDP
from mkernel.shapes.brep_wrapper import Brep
from mkernel.control.vicinity_picker import VicinityPicker
from mkernel.control.axis_picker.picker import AxisPicker

import gkernel.dtype.geometric as gt
from global_tools import FPSTimer


class BModeler(Modeler):
    def __init__(self, root_brep: Brep):
        super().__init__()
        self.__curr_brep = root_brep
        self.__last_button_stat = {i: 0 for i in range(3)}

        self.__frame_bffr = None
        self.__vp = VicinityPicker(offset=500)

    def listen(self, model, window, mouse, camera, cursor, id_picker, coord_picker):
        """
        listen each frame and activate draw logics
        :return:
        """
        left_button = mouse.get_button_status(0)
        # no ghost click
        if not self.active_exec_count and left_button == 1 and self.__last_button_stat[0] == 0:
            self.execute(command=self.__left_button_press,
                         model=model,
                         args=(window, camera, cursor, id_picker, coord_picker),
                         block_exec=True)
        self.__last_button_stat[0] = left_button

    def __left_button_press(self, window, camera, cursor, id_picker, coord_picker, model):
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

                self.execute(self.__render_guide_line, model,
                             args=(window, vrtx, camera, cursor, id_picker, coord_picker))
            else:
                print('ddd')

        else:
            print('selected')

    def __render_guide_line(self, window, svrtx, camera, cursor, id_picker, coord_picker, model):
        """
        renders guide line for line draw

        :param window:
        :param svrtx:
        :param camera:
        :param cursor:
        :param id_picker:
        :param coord_picker:
        :param model:
        :return:
        """
        # temporary drawing line
        xyz = svrtx.geo.xyz
        guid_line = model.add_lin(xyz, xyz)
        guid_line.do_render_id = False

        # draw snapping axis
        ap = AxisPicker(model, id_picker, coord_picker, cursor)
        axes = model.plane.axes
        for axis in axes:
            ap.append_axis(gt.Ray.from_pnt_vec(origin=svrtx.geo, normal=axis))

        keyboard = window.devices.keyboard
        mouse = window.devices.mouse
        left_button = 1

        timer = FPSTimer(target_fps=window.fps)
        while True:
            with timer:
                # check for exit
                if keyboard.get_key_status('esc') or mouse.get_button_status(1):
                    model.remove_shape(guid_line)
                    break

                # check for axis snap
                if keyboard.get_key_status('lshift'):
                    idx, tend = ap.pick_closest(camera.frusrum_ray(*cursor.pos_local.xy))
                    clr = [0, 0, 0, 1]
                    clr[idx] = 1
                    guid_line.clr = clr
                else:
                    with window.context.gl:
                        idx, tend = ap.pick_threshold()
                    # snap on to the axis, else pick vicinity
                    if idx is not None:
                        # snap on to the closest point and color
                        clr = [0, 0, 0, 1]
                        clr[idx] = 1
                        guid_line.clr = clr
                    else:
                        tend = self.__vp.pick(camera, cursor)[1]
                        guid_line.clr = 1, 1, 1, 1
                # update geometry
                guid_line.geo = gt.Lin.from_pnts(guid_line.geo.start, tend)

                # when left button pressed again
                if mouse.get_button_status(0) and not left_button:
                    break
                left_button = mouse.get_button_status(0)
        ap.delete()

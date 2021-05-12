from wkernel import Window
from mkernel import AModeler
from mkernel.control.util.vicinity_picker import VicinityPicker
import gkernel.dtype.geometric as gt


class MyWindow(Window):
    def __init__(self):
        super().__init__(500, 800, 'mywindow', None, None)
        self.framerate = 120
        camera = self.devices.cameras[0]
        camera.tripod.lookat(eye=(-100, -100, 100),
                             at=(0, 0, 0),
                             up=(0, 0, 1))
        # self.devices.cameras.attach_fps_dolly(0, 0)

        self.modeler = AModeler()
        self.model = self.modeler.add_model(parent=None)
        self.modeler.add_ground(self.model, [.5] * 4)
        self.modeler.add_pln(self.model, (0, 0, 0.001), (1, 0, 0), (0, 1, 0), (0, 0, 1))
        self.picker = VicinityPicker()

    def draw(self):
        with self.devices.frames[0] as df:
            df.clear(0, 0, 0, 1)
            df.clear_depth()

            with self.devices.cameras[0] as c:
                self.modeler.render()

                selection = self.picker.pick(gt.Pln(), c, self.devices.cursors[0])
                if selection:
                    key, point = selection
                    if key == 'xy':
                        clr = 0, 0, 1, 0.5
                    elif key == 'yz':
                        clr = 1, 0, 0, 0.5
                    else:
                        clr = 0, 1, 0, 0.5
                    self.modeler.add_raw(self.model, point).clr = clr

w = MyWindow()
w.run_all()

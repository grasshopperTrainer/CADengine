from wkernel import Window
from mkernel import Model
from mkernel.shapes.ground import Ground
from mkernel.modeler.vicinity_picker import VicinityPicker


class MyWindow(Window):
    def __init__(self):
        super().__init__(500, 800, 'mywindow', None, None)
        self.framerate = 120
        camera = self.devices.cameras[0]
        camera.tripod.lookat(eye=(-100, -100, 100),
                             at=(0, 0, 0),
                             up=(0, 0, 1))
        # self.devices.cameras.attach_fps_dolly(0, 0)

        self.model = Model()
        self.model.add_pln((0, 0, 0.001), (1, 0, 0), (0, 1, 0), (0, 0, 1))
        self.ground = Ground([.5] * 4)
        self.picker = VicinityPicker(500)

    def draw(self):
        with self.devices.frames[0] as df:
            df.clear(0, 0, 0, 1)
            df.clear_depth()

            with self.devices.cameras[0] as c:
                self.ground.render(c)
                self.model.render()

                k, P = self.picker.pick(c, self.devices.cursors[0])
                if k == 'xy':
                    clr = 0, 0, 1, 0.5
                elif k == 'yz':
                    clr = 1, 0, 0, 0.5
                else:
                    clr = 0, 1, 0, 0.5
                self.model.add_geo(P).clr = clr

w = MyWindow()
w.run_all()

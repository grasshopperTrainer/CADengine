"""
draw screen sized plans
"""

from wkernel import Window
from mkernel import AModeler


class MyWindow(Window):

    def __init__(self):
        super().__init__(500, 800, 'mywindow', None, None)
        camera = self.devices.cameras[0]
        camera.tripod.lookat(eye=(100, 50, 100),
                             at=(0, 0, 0),
                             up=(0, 0, 1))
        self.devices.cameras.attach_fps_dolly(0, 0)

        self.modeler = AModeler()
        self.model = self.modeler.add_model(parent=None)
        self.modeler.add_pln(self.model, (0, 0, 0.001), (1, 0, 0), (0, 1, 0), (0, 0, 1))
        self.modeler.add_pln(self.model, (10, 23, 10), (6, 4, 24), (5, 6, 10), (2, 100, 1))
        self.modeler.add_ground(self.model, (1, 1, 1, 1))

    def draw(self):
        with self.devices.frames[0] as df:
            df.clear(0, 0, 0, 1)
            df.clear_depth()

            with self.devices.cameras[0] as c:
                self.modeler.render()


w = MyWindow()
w.run_all()

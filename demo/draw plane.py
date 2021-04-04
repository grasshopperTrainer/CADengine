"""
draw screen sized plans
"""

from wkernel import Window
from mkernel import Model
from akernel.environmental.ground import Ground


class MyWindow(Window):
    def __init__(self):
        super().__init__(500, 800, 'mywindow', None, None)
        camera = self.devices.cameras[0]
        camera.tripod.lookat(eye=(100, 50, 100),
                             at=(0, 0, 0),
                             up=(0, 0, 1))
        self.devices.cameras.attach_fps_dolly(0, 0)

        self.model = Model()
        self.model.add_pln((0, 0, 0.001), (1, 0, 0), (0, 1, 0), (0, 0, 1))
        self.model.add_pln((10, 23, 10), (6, 4, 24), (5, 6, 10), (2, 100, 1))
        # self.model.add_pnt(0, 0, 0)
        self.ground = Ground([.5] * 4)

    def draw(self):
        with self.devices.frames[0] as df:
            df.clear(0, 0, 0, 1)
            df.clear_depth()

            with self.devices.cameras[0] as c:
                self.ground.render(c)
                self.model.render()


w = MyWindow()
w.run_all()

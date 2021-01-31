from doodler import *
from mkernel import Model, Pnt, Tgl, Plin
from wkernel import Window


class MyWindow(Window):
    def __init__(self):
        super().__init__(500, 1000, 'my window 1', monitor=None, shared=None)
        self.framerate = 60
        # enable camera move
        o = 200
        self.devices.cameras[0].tripod.lookat((-o, o, o / 2), (o, 0, 0), (0, 0, 1))
        self.devices.cameras.attach_fps_dolly(0)

        # create model
        self.model = Model()
        l = 100
        Plin([0, 0, 0], [l, 0, 0], [0, l, l], [l, l, l])
        k = 50
        Plin([k, 0, k], [0, k, k], [k, k, k*2])

    def draw(self, frame_count=None):
        with self.devices.panes[0] as p:
            with self.devices.cameras[0] as c:
                p.clear(.5, .5, .5, 0)
                self.model.test_render()


MyWindow().run_all(1)

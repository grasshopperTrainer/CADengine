from doodler import *
from mkernel import Model, Tgl,Lin
from wkernel import Window


class MyWindow(Window):
    def __init__(self):
        super().__init__(1000, 500, 'my window 1', monitor=None, shared=None)
        self.framerate = 60
        # enable camera move
        o = 50
        self.devices.cameras[0].tripod.lookat((200, 200, o/2), (0, 0, o/2), (0, 0, 1))
        self.devices.cameras.attach_fps_dolly(0)

        # create model
        self.model = Model()
        # create triangles
        e = 50
        l0 = Lin([0, 0, 0], [e, 0, 0])
        l1 = Lin([0, 0, 0], [0, e, 0])
        l2 = Lin([0, 0, 0], [0, 0, e])
        # set edge color
        i, a = 1, 0.5
        l0.clr = i, 0, 0, a
        l1.clr = 0, i, 0, a
        l2.clr = 0, 0, i, a
        # set thickness
        for l in (l0, l1, l2):
            l.thk = 10

    def draw(self, frame_count=None):
        with self.devices.panes[0] as p:
            with self.devices.cameras[0] as c:
                p.clear(.5, .5, .5, 1)
                self.model.test_render()

MyWindow().run_all(1)

from doodler import *
from mkernel import Model, Pnt
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
        p0 = Pnt(e, 0, 0)
        p1 = Pnt(0, e, 0)
        p2 = Pnt(0, 0, e)
        # set edge color
        i, a = 1, 1
        p0.clr = i, 0, 0, a
        p1.clr = 0, i, 0, a
        p2.clr = 0, 0, i, a
        # set thickness
        for p in (p0, p1, p2):
            p.dia = 10

    def draw(self, frame_count=None):
        with self.devices.panes[0] as p:
            with self.devices.cameras[0] as c:
                p.clear(.5, .5, .5, 1)
                self.model.test_render()

MyWindow().run_all()

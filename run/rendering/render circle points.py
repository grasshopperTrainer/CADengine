from doodler import *
from mkernel import Model, Pnt, Tgl
from wkernel import Window


class MyWindow(Window):
    def __init__(self):
        super().__init__(500, 1000, 'my window 1', monitor=None, shared=None)
        self.framerate = 60
        # enable camera move
        o = 200
        self.devices.cameras[0].tripod.lookat((-o, o, o/2), (o, 0, 0), (0, 0, 1))
        self.devices.cameras.attach_fps_dolly(0)

        # create model
        self.model = Model()
        # create triangles
        e = 50
        pnts = []
        pnts.append(Pnt(e, 0, 0))
        pnts.append(Pnt(0, e, 0))
        pnts.append(Pnt(0, 0, e))
        for i in range(20):
            e += 20
            pnts.append(Pnt(e, 0, 0))
        # set edge color
        i, a = 1, 1
        pnts[0].clr = i, 0, 0, a
        pnts[1].clr = 0, i, 0, a
        pnts[2].clr = 0, 0, i, a
        # set thickness
        c = 0.05
        for p in pnts[3:]:
            p.dia = 5
            p.clr = 1, 1, c, 1
            c += 0.05
            p.frm = p.FORM_CIRCLE
        # to check sizing
        Tgl([0, 0, 0], [100, 0, 0], [0, 100, 0])
        cp = Pnt(0, 0, 0)
        cp.clr = 1, 1, 0, 0.5
        cp.dia = 100

    def draw(self, frame_count=None):
        with self.devices.panes[0] as p:
            with self.devices.cameras[0] as c:
                p.clear(.5, .5, .5, 0)
                self.model.test_render()

MyWindow().run_all()

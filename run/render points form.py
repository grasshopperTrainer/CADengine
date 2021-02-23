from doodler import *
from mkernel import Model, Pnt, Tgl
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
        e = 50
        pnts = []
        for i in range(20):
            e += 20
            pnts.append(self.model.add_pnt(e, 0, 0))
        for p in pnts:
            p.dia = 10

        for i, p in enumerate(pnts):
            if i % 3 == 0:
                p.frm = p.FORM_SQUARE
            elif i % 3 == 1:
                p.frm = p.FORM_CIRCLE
            else:
                p.frm = p.FORM_TRIANGLE

    def draw(self, frame_count=None):
        with self.devices.panes[0] as p:
            with self.devices.cameras[0] as c:
                p.clear(.5, .5, .5, 0)
                self.model.render()


MyWindow().run_all(1)

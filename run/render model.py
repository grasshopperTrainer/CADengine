from doodler import *
from mkernel import Model, Tgl
from wkernel import Window


class MyWindow(Window):
    def __init__(self):
        super().__init__(500, 1000, 'my window 1', monitor=None, shared=None)
        self.framerate = 60
        # enable camera move
        o = 100
        self.devices.cameras[0].tripod.lookat((o, o, o), (0, 0, 0), (0, 0, 1))
        self.devices.cameras.attach_fps_dolly(0)

        # create model
        model1 = Model()
        model2 = Model()

        # model1.add_pnt(0, 0, 0)
        # model1.add_pnt(0, 10, 10)

        for i in range(10):
            pnt = model2.add_pnt(0, i * 10, i * 10)
            pnt.frm = pnt.FORM_CIRCLE
            pnt.dia = i
        model1.add_lin([0, 0, 0], [-20, 20, 20])
        model1.add_tgl([0, 0, 0], [10, 0, 0], [0, 10, 0])
        self.model1 = model1
        self.model2 = model2

    def draw(self, frame_count=None):
        with self.devices.panes[0] as p:
            with self.devices.cameras[0] as c:
                p.clear(.5, .5, .5, 1)
                # e = 100
                self.model1.render()
                self.model2.render()


MyWindow().run_all()

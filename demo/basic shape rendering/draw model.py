from mkernel import AModeler
from wkernel import Window


class MyWindow(Window):
    def __init__(self):
        super().__init__(500, 1000, 'my window 1', monitor=None, shared=None)
        self.framerate = 60
        # enable camera move
        o = 100
        self.devices.cameras[0].tripod.lookat((o, o, o), (0, 0, 0), (0, 0, 1))
        self.devices.cameras.attach_fps_dolly(0, 0)

        # create model
        self.modeler1 = AModeler()
        self.modeler2 = AModeler()

        self.model1 = self.modeler1.add_model(parent=None)
        self.model2 = self.modeler1.add_model(parent=None)

        for i in range(10):
            pnt = self.modeler2.add_pnt(self.model2, 0, i * 10, i * 10)
            pnt.frm = 'c'
            pnt.dia = i
        self.modeler1.add_lin(self.model1, [0, 0, 0], [-20, 20, 20])
        self.modeler1.add_tgl(self.model1, [0, 0, 0], [10, 0, 0], [0, 10, 0])

    def draw(self, frame_count=None):
        with self.devices.panes[0] as p:
            with self.devices.cameras[0] as c:
                p.clear(.5, .5, .5, 1)
                # e = 100
                self.modeler1.render()
                self.modeler2.render()


MyWindow().run_all()

from mkernel import AModeler
from wkernel import Window


class MyWindow(Window):
    def __init__(self):
        super().__init__(1000, 1000, 'my window 1', monitor=None, shared=None)
        self.framerate = 60
        # enable camera move
        o = 200
        self.devices.cameras[0].tripod.lookat(eye=(0, 0, o), at=(0, 0, 0), up=(0, 1, 0))
        self.devices.cameras.attach_fps_dolly(0, 0)

        # create model
        self.modeler = AModeler()
        self.model = self.modeler.add_model(parent=None)
        v0 = [0, 0, 0]
        v1 = [20, 0, 0]
        v2 = [25, 15, 0]
        v3 = [18, 20, 0]
        v4 = [10, 10, 0]
        v5 = [-10, 30, 0]
        v6 = [-5, 12, 0]
        v7 = [-20, 5, 0]
        vrtxs = [v0, v1, v2, v3, v4, v5, v6, v7, v0]
        # triangles draw
        self.modeler.add_tgl(self.model, v0, v1, v4)
        self.modeler.add_tgl(self.model, v1, v2, v4)
        self.modeler.add_tgl(self.model, v2, v3, v4)
        self.modeler.add_tgl(self.model, v0, v4, v6)
        self.modeler.add_tgl(self.model, v0, v6, v7)
        self.modeler.add_tgl(self.model, v4, v5, v6)

        for i in range(len(vrtxs)):
            x, y, z = vrtxs[i]
            vrtxs[i] = x, y+30, z
        p = self.modeler.add_pgon(self.model, *vrtxs)
        p.thk = 2

    def draw(self, frame_count=None):
        with self.devices.panes[0] as p:
            with self.devices.cameras[0] as c:
                p.clear(.5, .5, .5, 1)
                # e = 100
                self.modeler.render()

MyWindow().run_all()

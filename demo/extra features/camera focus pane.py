from mkernel import AModeler
from wkernel import Window


class MyWindow(Window):
    def __init__(self):
        super().__init__(1000, 2000, 'my window 1', monitor=None, shared=None)
        self.framerate = 60
        # enable camera move
        o = 200
        self.devices.cameras[0].tripod.lookat(eye=(0, 0, o), at=(0, 0, 0), up=(0, 1, 0))
        self.devices.cameras.factory.set_lrbt_dimension(-1, 1, -1, 1, 1, 1_000_000).set_frustum_shape('o').create()
        self.devices.panes.appendnew_pane(0.5, 0.5, 0.5, 0.5, self)
        self.devices.cameras[0].focus_pane(pane=self.devices.panes[1], focus=(0, 0, 0), clip_off=100)
        self.devices.cameras[1].focus_pane(pane=self.devices.panes[1], focus=(0, 0, 0), clip_off=100)

        # create model
        self.modeler = AModeler()
        self.model = self.modeler.add_model(parent=None)

        hpw, hph = [d/2 for d in self.devices.panes[1].size.xy]
        self.modeler.add_pnt(self.model, 0, 0, 0)
        for dx in (-1, 1):
            for dy in (-1, 1):
                for z in range(-500, 1, 100):
                    p = self.modeler.add_pnt(self.model, hpw*dx, hph*dy, z)
                    p.frm = 'c'
                    p.dia = 30

    def draw(self, frame_count=None):
        with self.devices.panes[1] as p:
            with self.devices.cameras[0] as c:
                p.clear(.5, .5, .5, 1)
                self.modeler.render()

MyWindow().run_all(1)

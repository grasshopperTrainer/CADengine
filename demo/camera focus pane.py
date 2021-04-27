from mkernel import AModel
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
        model1 = AModel()
        self.model1 = model1
        hpw, hph = [d/2 for d in self.devices.panes[1].size.xy]
        model1.add_pnt(0, 0, 0)
        for dx in (-1, 1):
            for dy in (-1, 1):
                for z in range(-500, 1, 100):
                    p = model1.add_pnt(hpw*dx, hph*dy, z)
                    p.frm = p.FORM_CIRCLE
                    p.dia = 30

    def draw(self, frame_count=None):
        with self.devices.panes[1] as p:
            with self.devices.cameras[0] as c:
                p.clear(.5, .5, .5, 1)
                # e = 100
                self.model1.render()

MyWindow().run_all(1)

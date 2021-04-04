from gkernel.dtype.geometric.brep import Brep
from mkernel import Model
from wkernel import Window


class MyWindow(Window):
    def __init__(self):
        super().__init__(1000, 1000, 'my window 1', monitor=None, shared=None)
        self.framerate = 60
        # enable camera move
        o = 200
        # self.devices.cameras[0].tripod.lookat(eye=(0, 0, o), at=(0, 0, 0), up=(0, 1, 0))
        self.devices.cameras[0].focus_pane(pane=self.devices.panes[0], focus=(0, 0, 0), clip_off=100)

        # create model
        model = Model()
        brep = model.add_brep()
        v = brep.add_vrtx(0, 0, 0)
        print(v)
        self.model = model

    def draw(self, frame_count=None):
        with self.devices.panes[0] as p:
            with self.devices.cameras[0] as c:
                p.clear(.5, .5, .5, 1)
                # e = 100
                self.model.render()


MyWindow().run_all(1)
from doodler import *
from mkernel import Model, Tgl
from wkernel import Window
import gkernel.dtype.geometric as gt
from gkernel.color import *


class MyWindow(Window):
    def __init__(self):
        super().__init__(1000, 1000, 'my window 1', monitor=None, shared=None)
        self.framerate = 60
        # enable camera move
        o = 200
        # self.devices.cameras[0].tripod.lookat(eye=(0, 0, o), at=(0, 0, 0), up=(0, 1, 0))
        self.devices.cameras[0].focus_pane(pane=self.devices.panes[0], focus=(0, 0, 0), clip_off=100)

        # create model
        model1 = Model()
        self.model1 = model1
        pw, ph = self.devices.panes[0].size
        n = 20
        nw, nh = pw//n, ph//n
        for x in range(-pw//2+nw, pw//2-nw+1, nw):
            for y in range(-ph//2+nh, ph//2-nh+1, nh):
                p = model1.add_pnt(x, y, 0)
                p.frm = p.FORM_CIRCLE
                p.dia = 10


    def draw(self, frame_count=None):
        with self.devices.panes[0] as p:
            with self.devices.cameras[0] as c:
                p.clear(.5, .5, .5, 1)
                # e = 100
                self.model1.render()

MyWindow().run_all(1)

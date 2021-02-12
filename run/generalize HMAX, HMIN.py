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
        plns = []
        self.model1 = model1
        pw, ph = self.devices.panes[0].size
        n = 6
        nw, nh = pw // n, ph // n
        for x in range(-pw // 2 + nw, pw // 2 - nw + 1, nw):
            for y in range(-ph // 2 + nh, ph // 2 - nh + 1, nh):
                plns.append(gt.Pln(o=(x, y, 0)))
                model1.add_pnt(x, y, 1).clr = ClrRGBA(1, 1, 0, 1)

        e = 100
        q = e / 4
        h = e / 2
        o = e / 10
        t = e / 3
        pgons = []

        # triangle
        pgons.append(gt.Pgon((0, 0, 0),
                             (e, 0, 0),
                             (0, e, 0),
                             (0, 0, 0)))
        # rectangle
        pgons.append(gt.Pgon((0, 0, 0),
                             (e, 0, 0),
                             (e, e, 0),
                             (0, e, 0),
                             (0, 0, 0)))
        # block
        pgons.append(gt.Pgon((0, 0, 0),
                             (h, 0, 0),
                             (h, h, 0),
                             (e, h, 0),
                             (e, e, 0),
                             (0, e, 0),
                             (0, 0, 0)))
        # hills
        pgons.append(gt.Pgon((0, 0, 0),
                             (e, 0, 0),
                             (e, h, 0),
                             (q * 3, e, 0),
                             (q * 2, h, 0),
                             (q, e, 0),
                             (0, h, 0),
                             (0, 0, 0)))
        # beanie
        pgons.append(gt.Pgon((0, 0, 0),
                             (e, 0, 0),
                             (e, h, 0),
                             (q * 3, e, 0),
                             (q, e, 0),
                             (0, h, 0),
                             (0, 0, 0)))
        # cat
        pgons.append(gt.Pgon((0, 0, 0),
                             (e, 0, 0),
                             (e, h, 0),
                             (q * 3, e, 0),
                             (q * 3, h, 0),
                             (q, h, 0),
                             (q, e, 0),
                             (0, h, 0),
                             (0, 0, 0)))
        # reverse house
        pgons.append(gt.Pgon((h, 0, 0),
                             (e, h, 0),
                             (e, e, 0),
                             (0, e, 0),
                             (0, h, 0),
                             (h, 0, 0)))
        # left dialog
        pgons.append(gt.Pgon((q, 0, 0),
                             (h, h, 0),
                             (e, h, 0),
                             (e, e, 0),
                             (0, e, 0),
                             (0, h, 0),
                             (q, 0, 0)))
        # diamond
        pgons.append(gt.Pgon((h, 0, 0),
                             (e, h, 0),
                             (h, e, 0),
                             (0, h, 0),
                             (h, 0, 0)))
        # quad triangle
        pgons.append(gt.Pgon((h, 0, 0),
                             (e, 0, 0),
                             (h, e, 0),
                             (0, 0, 0),
                             (h, 0, 0)))
        # right dialog
        pgons.append(gt.Pgon((3 * q, 0, 0),
                             (e, h, 0),
                             (e, e, 0),
                             (0, e, 0),
                             (0, h, 0),
                             (h, h, 0),
                             (3 * q, 0, 0)))
        # torn paper
        pgons.append(gt.Pgon((0, 0, 0),
                             (-q, -q, 0),
                             (0, -q, 0),
                             (e, -q, 0),

                             (e-q, h, 0),
                             (e, e, 0),

                             (-q, e, 0),
                             (0, h+q, 0),
                             (-q, q, 0),
                             (0, 0, 0)))
        # flag right
        pgons.append(gt.Pgon((0, 0, 0),
                             (e, 0, 0),
                             (3 * q, h, 0),
                             (e, e, 0),
                             (0, e, 0),
                             (0, 0, 0)))
        # tick
        pgons.append(gt.Pgon((0, 0, 0),
                             (e, e, 0),
                             (0, -h, 0),
                             (-h, 0, 0),
                             (0, 0, 0)))
        # cravas
        pgons.append(gt.Pgon((0, 0, 0),
                             (q, h, 0),
                             (h, q, 0),
                             (e, e, 0),
                             (-h, e, 0),
                             (0, 0, 0)))
        # mountain
        pgons.append(gt.Pgon((0, 0, 0),
                             (e, 0, 0),
                             (e-q, 2*q, 0),
                             (e-q, q, 0),
                             (h, 3*q, 0),
                             (h, 2*q, 0),
                             (q, e, 0),
                             (0, 0, 0)))
        # bow tie
        pgons.append(gt.Pgon((0, 0, 0),
                             (h, q, 0),
                             (e, 0, 0),
                             (e, e, 0),
                             (h, 3*q, 0),
                             (0, e, 0),
                             (0, 0, 0)))
        # pants
        pgons.append(gt.Pgon((0, 0, 0),
                             (q, 0, 0),
                             (h, h, 0),
                             (3 * q, 0, 0),
                             (e, 0, 0),
                             (e, e, 0),
                             (0, e, 0),
                             (0, 0, 0)))
        # bad m
        pgons.append(gt.Pgon((0, 0, 0),
                             (q, 0, 0),
                             (q, h, 0),
                             (h, q, 0),
                             (3*q, h, 0),
                             (3*q, 0, 0),
                             (e, 0, 0),
                             (e, e, 0),
                             (0, e, 0),
                             (0, 0, 0)))
        # M
        pgons.append(gt.Pgon((0, 0, 0),
                             (q, 0, 0),
                             (q, h, 0),
                             (1.5*q, q, 0),
                             (2.5*q, q, 0),
                             (3 * q, h, 0),
                             (3 * q, 0, 0),
                             (e, 0, 0),
                             (e, e, 0),
                             (3*q, e, 0),
                             (2.2*q, h, 0),
                             (1.8*q, h, 0),
                             (q, e, 0),
                             (0, e, 0),
                             (0, 0, 0)))
        # N
        pgons.append(gt.Pgon((0, 0, 0),
                             (q, 0, 0),
                             (q, h, 0),
                             (3 * q, 0, 0),
                             (e, 0, 0),
                             (e, e, 0),
                             (3 * q, e, 0),
                             (3 * q, h, 0),
                             (q, e, 0),
                             (0, e, 0),
                             (0, 0, 0)))
        # drill
        pgons.append(gt.Pgon((h-o, 0, 0),
                             (h+o, 0, 0),
                             (2*t, h, 0),
                             (2.5 * t, h, 0),
                             (e, h+q, 0),
                             (e, e, 0),
                             (0, e, 0),
                             (0, h+q, 0),
                             (0.5 * t, h, 0),
                             (t, h, 0),
                             (h-o, 0, 0)))
        # gate
        pgons.append(gt.Pgon((0, 0, 0),
                             (t, 0, 0),
                             (t, h, 0),
                             (2*t, h, 0),
                             (2*t, 0, 0),
                             (e, 0, 0),
                             (e, e, 0),
                             (0, e, 0),
                             (0, 0, 0)))
        # # thin leg
        pgons.append(gt.Pgon((0, 0, 0),
                             (t, 0, 0),
                             (t, h, 0),
                             (2 * t, h, 0),
                             (2 * t, 0, 0),
                             (e, e, 0),
                             (0, e, 0),
                             (0, 0, 0)))

        # nepal
        pgons.append(gt.Pgon((0, 0, 0),
                             (e, q, 0),
                             (q, h, 0),
                             (3 * q, 3 * q, 0),
                             (0, e, 0),
                             (0, 0, 0)))

        for pgon, pln in zip(pgons, plns):
            model1.add_geo(pln.orient(pgon)).thk = 5

    def draw(self, frame_count=None):
        with self.devices.panes[0] as p:
            with self.devices.cameras[0] as c:
                p.clear(.5, .5, .5, 1)
                # e = 100
                self.model1.render()


MyWindow().run_all(1)

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
        n = 7
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

        # A
        pgons.append(gt.Pgon((0, 0, 0),
                             (q, 0, 0),
                             (t, q, 0),
                             (2 * t, q, 0),
                             (3 * q, 0, 0),
                             (e, 0, 0),
                             (h, e, 0),
                             (0, 0, 0)))
        # B
        k = e - 3 * o
        pgons.append(gt.Pgon((0, 0, 0),
                             (k, 0, 0),
                             (e, o, 0),
                             (e, h - o, 0),
                             (k, h, 0),
                             (e, h + o, 0),
                             (e, e - o, 0),
                             (k, e, 0),
                             (0, e, 0),
                             (0, 0, 0)))
        # C
        pgons.append(gt.Pgon((q, 0, 0),
                             (h, 0, 0),
                             (e, 0, 0),
                             (e, q, 0),
                             (h, q, 0),
                             (t, t, 0),
                             (t, 2*t, 0),
                             (h, e-q, 0),
                             (e, e-q, 0),
                             (e, e, 0),
                             (q, e, 0),
                             (0, e-q, 0),
                             (0, q, 0),
                             (q, 0, 0)))
        # D
        pgons.append(gt.Pgon((0, 0, 0),
                             (3*q, 0, 0),
                             (e, q, 0),
                             (e, e-q, 0),
                             (e-q, e, 0),
                             (0, e, 0),
                             (0, 0, 0)))
        # E
        k = e/5
        pgons.append(gt.Pgon((0, 0, 0),
                             (e, 0, 0),
                             (e, k, 0),
                             (h, k, 0),
                             (h, 2*k, 0),
                             (e, 2*k, 0),
                             (e, 3*k, 0),
                             (h, 3*k, 0),
                             (h, 4*k, 0),
                             (e, 4*k, 0),
                             (e, e, 0),
                             (0, e, 0),
                             (0, 0, 0)))
        # F
        k = e / 5
        pgons.append(gt.Pgon((0, 0, 0),
                             (t, 0, 0),
                             (t, q, 0),
                             (2*t, q, 0),
                             (2*t, h, 0),
                             (t, h, 0),
                             (t, 3*q, 0),
                             (e, 3*q, 0),
                             (e, e, 0),
                             (0, e, 0),
                             (0, 0, 0)))
        # G
        pgons.append(gt.Pgon((0, 0, 0),
                             (e, 0, 0),
                             (e, 2*t-o, 0),
                             (e-q-o, 2*t-o, 0),
                             (e-q, t, 0),
                             (q, t, 0),
                             (q, 2*t, 0),
                             (e, 2*t, 0),
                             (e, e, 0),
                             (0, e, 0),
                             (0, 0, 0)))
        # H
        pgons.append(gt.Pgon((0, 0, 0),
                             (t, 0, 0),
                             (t, t, 0),
                             (2 * t, t, 0),
                             (2 * t, 0, 0),
                             (e, 0, 0),
                             (e, e, 0),
                             (2*t, e, 0),
                             (2*t, 2*t, 0),
                             (t, 2*t, 0),
                             (t, e, 0),
                             (0, e, 0),
                             (0, 0, 0)))
        # I
        pgons.append(gt.Pgon((0, 0, 0),
                             (e, 0, 0),
                             (e, t, 0),
                             (2*t, t, 0),
                             (2*t, 2*t, 0),
                             (e, 2*t, 0),
                             (e, e, 0),
                             (0, e, 0),
                             (0, 2*t, 0),
                             (t, 2*t, 0),
                             (t, t, 0),
                             (0, t, 0),
                             (0, 0, 0)))
        # J
        pgons.append(gt.Pgon((q, 0, 0),
                             (2*t, 0, 0),
                             (e-o, t, 0),
                             (e-o, e-q, 0),
                             (e, e-q, 0),
                             (e, e, 0),
                             (h, e, 0),
                             (h, e-q, 0),
                             (2*t, e-q, 0),
                             (2*t, h, 0),
                             (h, q, 0),
                             (t, q, 0),
                             (t, h, 0),
                             (0, h, 0),
                             (0, q, 0),
                             (q, 0, 0)))
        # K
        pgons.append(gt.Pgon((0, 0, 0),
                             (t, 0, 0),
                             (t, q, 0),
                             (h, 0, 0),
                             (e, 0, 0),
                             (h, h, 0),
                             (e, e-q, 0),
                             (e, e, 0),
                             (t, e-t, 0),
                             (t, e, 0),
                             (0, e, 0),
                             (0, 0, 0)))
        # L
        pgons.append(gt.Pgon((0, 0, 0),
                             (e, 0, 0),
                             (e, t, 0),
                             (t, t, 0),
                             (t, e, 0),
                             (0, e, 0),
                             (0, 0, 0)))
        # M
        pgons.append(gt.Pgon((0, 0, 0),
                             (q, 0, 0),
                             (q, h, 0),
                             (1.5 * q, q, 0),
                             (2.5 * q, q, 0),
                             (3 * q, h, 0),
                             (3 * q, 0, 0),
                             (e, 0, 0),
                             (e, e, 0),
                             (3 * q, e, 0),
                             (2.2 * q, h, 0),
                             (1.8 * q, h, 0),
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
        # O
        pgons.append(gt.Pgon((q, 0, 0),
                             (e-q, 0, 0),
                             (e, q, 0),
                             (e, e-q, 0),
                             (e-q, e, 0),
                             (q, e, 0),
                             (0, e-q, 0),
                             (0, q, 0),
                             (q, 0, 0)))
        # P
        pgons.append(gt.Pgon((0, 0, 0),
                             (q, 0, 0),
                             (q, h, 0),
                             (e, h, 0),
                             (e, e, 0),
                             (0, e, 0),
                             (0, 0, 0)))
        # Q
        pgons.append(gt.Pgon((q, 0, 0),
                             (h+o, 0, 0),
                             (t*2+o, o, 0),
                             (e - o, 0, 0),
                             (e, o, 0),
                             (e-o, t-o, 0),
                             (e, h-o, 0),
                             (e, e - q, 0),
                             (e - q, e, 0),
                             (q, e, 0),
                             (0, e - q, 0),
                             (0, q, 0),
                             (q, 0, 0)))
        # R
        pgons.append(gt.Pgon((0, 0, 0),
                             (h, 0, 0),
                             (h, q, 0),
                             (e-q, 0, 0),
                             (e, 0, 0),
                             (e-q, h, 0),
                             (e, h, 0),
                             (e, e, 0),
                             (0, e, 0),
                             (0, 0, 0)))
        # S
        pgons.append(gt.Pgon((0, 0, 0),
                             (e, 0, 0),
                             (e, e-t, 0),
                             (t, e-t, 0),
                             (t, e-t+o, 0),
                             (e, e-t+o, 0),
                             (e, e, 0),
                             (0, e, 0),
                             (0, t, 0),
                             (e-t, t, 0),
                             (e-t, t-o, 0),
                             (0, t-o, 0),
                             (0, 0, 0)))
        # T
        pgons.append(gt.Pgon((q, 0, 0),
                             (e-q, 0, 0),
                             (e-q, e-q, 0),
                             (e, e-q, 0),
                             (e, e, 0),
                             (0, e, 0),
                             (0, e-q, 0),
                             (q, e-q, 0),
                             (q, 0, 0)))
        # U
        pgons.append(gt.Pgon((q, 0, 0),
                             (e - q, 0, 0),
                             (e, q, 0),
                             (e, e, 0),
                             (e-t, e, 0),
                             (e-t, h, 0),
                             (t, h, 0),
                             (t, e, 0),
                             (0, e, 0),
                             (0, q, 0),
                             (q, 0, 0)))
        # V
        pgons.append(gt.Pgon((q, 0, 0),
                             (e-q, 0, 0),
                             (e, e, 0),
                             (e-t, e, 0),
                             (h, h, 0),
                             (t, e, 0),
                             (0, e, 0),
                             (q, 0, 0)))
        # W
        f = e/5
        pgons.append(gt.Pgon((f, 0, 0),
                             (f * 2, 0, 0),
                             (h, h, 0),
                             (f * 3, 0, 0),
                             (f * 4, 0, 0),
                             (e, e, 0),
                             (e-f, e, 0),
                             (e-f*1.5, h, 0),
                             (f * 3, e, 0),
                             (f * 2, e, 0),
                             (f * 1.5, h, 0),
                             (f, e, 0),
                             (0, e, 0),
                             (f, 0, 0)))
        # X
        pgons.append(gt.Pgon((0, 0, 0),
                             (q, 0, 0),
                             (h, t, 0),
                             (e, 0, 0),
                             (e, q, 0),
                             (e-t, h, 0),
                             (e, e, 0),
                             (e-q, e, 0),
                             (h, e-t, 0),
                             (0, e, 0),
                             (0, e-q, 0),
                             (t, h, 0),
                             (0, 0, 0)))
        # Y
        pgons.append(gt.Pgon((t, 0, 0),
                             (t * 2, 0, 0),
                             (t * 2, h, 0),
                             (e, e - t, 0),
                             (e, e, 0),
                             (h, e - q, 0),
                             (0, e, 0),
                             (0, e - t, 0),
                             (t, h, 0),
                             (t, 0, 0)))
        # Z
        pgons.append(gt.Pgon((0, 0, 0),
                             (e, 0, 0),
                             (e, q, 0),
                             (h, q, 0),
                             (e, e, 0),
                             (0, e, 0),
                             (0, e-q, 0),
                             (h, e-q, 0),
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

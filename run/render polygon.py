from doodler import *
from mkernel import Model, Tgl
from wkernel import Window
import gkernel.dtype.geometric as gt

class MyWindow(Window):
    def __init__(self):
        super().__init__(500, 1000, 'my window 1', monitor=None, shared=None)
        self.framerate = 60
        # enable camera move
        o = 75
        self.devices.cameras[0].tripod.lookat(eye=(0, 0, o), at=(0, 0, 0), up=(0, 1, 0))
        self.devices.cameras.attach_fps_dolly(0)

        # create model
        model1 = Model()
        v0 = [0, 0, 0]
        v1 = [20, 0, 0]
        v2 = [25, 15, 0]
        v3 = [18, 20, 0]
        v4 = [10, 10, 0]
        v5 = [-10, 30, 0]
        v6 = [-5, 12, 0]
        v7 = [-20, 5, 0]
        model1.add_tgl(v0, v1, v4)
        model1.add_tgl(v1, v2, v4)
        model1.add_tgl(v2, v3, v4)
        model1.add_tgl(v0, v4, v6)
        model1.add_tgl(v0, v6, v7)
        model1.add_tgl(v4, v5, v6)


        MAX, MIN, HMAX, HMIN, HORI, INTR = range(6)
        vs = [v0, v1, v2, v3, v4, v5, v6, v7]
        vs = [gt.Pnt(*v) for v in vs]

        for i in range(len(vs)):
            # stage 1
            # determine catagory
            left, this, right = vs[i-1], vs[i], vs[(i+1) % len(vs)]
            cat = None
            if left.y < this.y:           # left below current
                if right.y < this.y:       # right below current
                    cat = MAX
                elif right.y == this.y:    # right horizontal
                    cat = HMAX
                else:                           # right above
                    cat = INTR
            elif left.y == this.y:        # left horizontal
                if right.y < this.y:       # right below current
                    cat = HMAX
                elif right.y == this.y:    # right horizontal
                    cat = HORI
                else:                           # right upper
                    cat = HMIN
            else:                               # left upper current
                if right.y < this.y:       # right below current
                    cat = INTR
                elif right.y == this.y:    # right horizontal
                    cat = HMIN
                else:                           # right upper
                    cat = MIN

            norm = gt.Vec.cross(right - this, left - this)
            sweep_line = None
            if cat in (HORI, HMIN, HMAX):
                sweep_line = None
            elif cat in (MIN, MAX):
                if 0 < gt.Vec.dot(gt.ZVec(), norm):
                    sweep_line = None
                else:
                    sweep_line = 'bi'
            elif cat == INTR:
                if left.y < right.y:
                    sweep_line = 'left'
                else:
                    sweep_line = 'right'
            print(vs[i], cat, sweep_line)

        self.model1 = model1

    def draw(self, frame_count=None):
        with self.devices.panes[0] as p:
            with self.devices.cameras[0] as c:
                p.clear(.5, .5, .5, 1)
                # e = 100
                self.model1.render()

MyWindow().run_all(1)

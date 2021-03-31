import gkernel.dtype.geometric as gt

from mkernel import Model
from wkernel import Window
import random


class MyWindow(Window):
    def __init__(self):
        super().__init__(1000, 500, 'my window 1', monitor=None, shared=None)
        self.framerate = 60

        self.fcount = 0
        # enable camera move
        self.devices.cameras[0].tripod.lookat((0, 0, 2000), (0, 0, 0), (0, 1, 0))
        d = self.devices.cameras.attach_fps_dolly(0, 0)
        d.move_boost = 10
        d.move_spd = 5
        # create model
        self.model = Model()

        self.num_scratch = 0
        self.ori = None
        self.lin_vec = None
        self.offset_vec = None
        self.thk = None

    def draw(self):
        if not self.num_scratch:
            self.ori = gt.Pnt(*(random.randint(-1500, 1500) for _ in range(2)), random.randint(-200, 200))
            self.lin_vec = gt.Vec(*(random.uniform(-1, 1) for _ in range(2))).amplify(random.randint(200, 500))
            self.offset_vec = gt.Vec.cross(gt.ZVec(), self.lin_vec).amplify(random.randint(10, 100))
            self.num_scratch = random.randint(0, 25)
            self.thk = random.randint(0, 8)

        if self.fcount % 3 == 0:
            geo = gt.Lin.from_pnt_vec(self.ori + self.offset_vec * self.num_scratch, self.lin_vec)
            lin = self.model.add_geo(geo)
            lin.thk = self.thk
            self.num_scratch -= 1
        self.fcount += 1

        with self.devices.panes[0] as p:
            with self.devices.cameras[0] as c:
                p.clear(.5, .5, .5, 1)
                self.model.render()


MyWindow().run_all()

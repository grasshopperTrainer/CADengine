from UVT import Window, gl
import numpy as np
from doodler import *
import UVT.pipeline.nodes as node


class W(Window):
    def __init__(self):
        super().__init__(500, 300, 'window1')

    def setup(self):
        print('setting up')
        self.framerate = 10
        self.views.new_view(0.25, 0.25, 0.5, 0.5)
        # self.views.new_view(0, 0, 0.5, 0.5)
        self.cameras[0].tripod.lookat((100, 100, 100), (0, 0, 0), (0, 0, 1))
        self.cameras[0].set_fps_dolly(self)

    def draw(self):
        super().draw()
        with self.views[1] as v:
            v.clear(0, 1, 0.5, 1)
            with self.cameras[0] as c:
                # x, y = self.devices.mouse.in_view(v, False)
                a = 100
                triangle((0, 0, 0), (a, 0, 0), (0, a, 0))
                triangle((0, 0, 0), (-a, 0, 0), (0, -a, 0))
                triangle((a, a, 0), (a, 0, 0), (0, a, 0))
w = W()
w.run()

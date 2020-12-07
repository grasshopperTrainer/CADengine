from UVT import Window, gl
import numpy as np
from doodler import *
import UVT.pipeline.nodes as node


class W(Window):
    def __init__(self):
        super().__init__(200, 300, 'window1')

    def setup(self):
        print('setting up')
        self.framerate = 2
        self.views.new_view(0.25, 0.25, 0.5, 0.5)
        # self.views.new_view(0, 0, 0.5, 0.5)

    def draw(self):
        super().draw()
        with self.views[0] as v:
            v.clear()
        with self.views[1] as v:
            v.clear(0, 1, 0, 1)
            x, y = self.devices.mouse.in_view(v, False)

w = W()
w.run()

from UVT import Window, gl
from doodle import *
import UVT.pipeline.nodes as node

class W(Window):
    def __init__(self):
        super().__init__(500, 500, 'window1')

    def setup(self):
        print('setting up')
        self._inited = False
        self.framerate = 4
        self.count = 0

    def draw(self):
        super().draw()
        with self.cameras[0]:
            a = 10
            triangle((0,0,0), (a,0,0), (0,a,0))
            triangle((0,0,0), (-a,0,0), (0,-a,0))
            triangle((a,a,0), (a,0,0), (0,a,0))

w = W()
w.run(1)

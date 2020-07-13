from UVT import Window, gl
from UVT.doodle import *
import UVT.pipeline.nodes as node

class W(Window):
    def __init__(self):
        super().__init__(200, 200, 'window1')

    def setup(self):
        print('setting up')
        self._inited = False
        self.framerate = 4
        self.count = 0

    def draw(self):
        super().draw()
        triangle((0,0,0), (1,0,0), (0,1,0))
        triangle((0,0,0), (-1,0,0), (0,-1,0))

w = W()
w.run()

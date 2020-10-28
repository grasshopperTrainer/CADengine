from UVT import Window, gl
from doodler import *
import UVT.pipeline.nodes as node

class W(Window):
    def __init__(self):
        super().__init__(2000, 1000, 'window1')

    def setup(self):
        print('setting up')
        self._inited = False
        self.framerate = 30
        self.count = 0
        self.cameras[0].tripod.lookat((100,100,100), (0,0,0),(0,0,1))
        self.cameras.set_fps_dolly(self.cameras[0])

    def draw(self):
        super().draw()
        self._views
        with self.cameras[0]:
            a = 100
            triangle((0,0,0), (a,0,0), (0,a,0))
            triangle((0,0,0), (-a,0,0), (0,-a,0))
            triangle((a,a,0), (a,0,0), (0,a,0))

w = W()
w.run()

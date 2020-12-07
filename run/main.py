from UVT import Window, gl
from doodler import *
import UVT.pipeline.nodes as node

class W(Window):
    def __init__(self):
        super().__init__(500, 500, 'window1')

    def setup(self):
        print('setting up')
        self._inited = False
        self.framerate = 10
        self.count = 0
        self.cameras[0].tripod.lookat((100,100,100), (0,0,0),(0,0,1))
        self.cameras[0].set_fps_dolly(self)
        self.views.new_view(0.5, 0.5, 0.5, 0.5)

    def draw(self):
        super().draw()
        with self.views[0] as v:
            with self.cameras[0]:
                pass
                a = 100
                triangle((0,0,0), (a,0,0), (0,a,0))
                triangle((0,0,0), (-a,0,0), (0,-a,0))
                triangle((a,a,0), (a,0,0), (0,a,0))
                # print(self._views[0]._glyph.posx)

w = W()
w.run()

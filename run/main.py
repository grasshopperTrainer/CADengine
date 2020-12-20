from wkernel import Window, gl
from doodler import *
import wkernel.pipeline.nodes as node


class W(Window):
    def __init__(self):
        super().__init__(500, 500, 'window1')

    def setup(self):
        print('setting up')
        self._inited = False
        self.framerate = 30
        self.count = 0
        self.cameras[0].tripod.lookat((100, 100, 100), (0, 0, 0), (0, 0, 1))
        self.cameras[0].set_fps_dolly(self)
        # self.views.new_view(0.5, 0.5, 0.5, 0.5)

    def draw(self):
        super().draw()
        with self.views[0] as v:
            v.clear(.5, .5, .5, 1)
            with self.cameras[0]:
                print()
                print('drawing...')
                # print(self.cameras[0].tripod.out_plane.r.arr)
                # print(self.cameras[0].tripod.VM.r)
                # print(self.cameras[0].body.PM)
                # print(self.cameras[0].tripod.out_plane.r.arr)
                #         pass
                a = 100
                z = 0

                triangle((0, -a, z), (-a, 0, z), (-a, -a, z))
                triangle((0, 0, z), (a, 0, z), (0, a, z))
                # triangle((0,0,z), (-a,0,z), (0,-a,z))
                # triangle((-a,-a,z), (a,0,z), (0,a,z))
        #         # print(self._views[0]._glyph.posx)


w = W()
w.run()

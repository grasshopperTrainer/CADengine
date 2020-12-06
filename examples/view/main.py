from UVT import Window, gl
import numpy as np
from doodler import *
import UVT.pipeline.nodes as node


class W(Window):
    def __init__(self):
        super().__init__(500, 500, 'window1')

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
            m = v.glyph.trans_matrix.r.I.trnsf_matrix._data

            s = np.array([[1/500, 0, 0, 0],
                          [0, 1/500, 0, 0],
                          [0, 0, 1, 0],
                          [0,0,0,1]])
            p = np.array([[self.devices.mouse.current_pos[0]],
                          [self.devices.mouse.current_pos[1]],
                          [0],
                          [1]])
            print(s.dot(m.dot(p)))
            # with self.cameras[0]:
            #     pass
        # with self.views[1] as v:
        #     v.clear(0, 0, 0.5, 0.5)
        # with self.views[2] as v:
        #     v.clear(0, 0.5, 0, 0.5)
        #     print(v.rel_mouse_pos())
w = W()
w.run()

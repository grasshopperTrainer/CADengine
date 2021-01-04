from doodler import *
from wkernel import Window


class MyWindow(Window):
    def __init__(self):
        super().__init__(500, 500, 'my window 1', monitor=None, shared=None)
        self.framerate = 30

        # enable camera move
        self.cameras[0].tripod.lookat((100, 100, 100), (0, 0, 0), (0, 0, 1))
        self.cameras.attach_fps_dolly(0)

    def draw(self, frame_count=None):
        print('rendering')
        with self.panes[0] as v:
            with self.cameras[0]:
                v.clear(.5, .5, .5, 1)
                e = 100
                x = triangle([0, 0, 0],
                             [e, 0, 0],
                             [0, e, 0])
                y = triangle([0, 0, 0],
                             [0, e, 0],
                             [0, 0, e])
                z = triangle([0, 0, 0],
                             [e, 0, 0],
                             [0, 0, e])

MyWindow().run()

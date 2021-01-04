from doodler import *
from mkernel import Model, Tgl
from wkernel import Window


class MyWindow(Window):
    def __init__(self):
        super().__init__(500, 500, 'my window 1', monitor=None, shared=None)
        self.framerate = 120

        # enable camera move
        self.cameras[0].tripod.lookat((100, 100, 100), (0, 0, 0), (0, 0, 1))
        self.cameras.attach_fps_dolly(0)

        # create model
        self.coord_indc = Model()
        e = 100
        self.coord_indc.append_shape(Tgl([0, 0, 0], [e, 0, 0], [0, e, 0]))
        self.coord_indc.append_shape(Tgl([0, 0, 0], [0, e, 0], [0, 0, e]))
        self.coord_indc.append_shape(Tgl([0, 0, 0], [e, 0, 0], [0, 0, e]))

    def draw(self, frame_count=None):
        with self.panes[0] as v:
            with self.cameras[0] as c:
                v.clear(.5, .5, .5, 1)
                self.coord_indc.render()
                self.coord_indc.intersect(c.frusrum_ray(*v.local_cursor()))
                e = 100
                triangle([0, 0, 0], [e, 0, 0], [0, e, 0])
                triangle([0, 0, 0], [0, e, 0], [0, 0, e])
                triangle([0, 0, 0], [e, 0, 0], [0, 0, e])
MyWindow().run()

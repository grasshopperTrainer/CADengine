from doodler import *
from mkernel import Model, Tgl
from wkernel import Window


class MyWindow(Window):
    def __init__(self):
        super().__init__(500, 500, 'my window 1', monitor=None, shared=None)
        self.framerate = 60
        # enable camera move
        self.cameras[0].tripod.lookat((100, 100, 100), (0, 0, 0), (0, 0, 1))
        self.cameras.attach_fps_dolly(0)

        # create model
        self.model = Model()
        e = 100
        self.model.append_shape(Tgl([0, 0, 0], [e, 0, 0], [0, e, 0]))
        self.model.append_shape(Tgl([0, 0, 0], [0, e, 0], [0, 0, e]))
        self.model.append_shape(Tgl([0, 0, 0], [e, 0, 0], [0, 0, e]))
    #
    def draw(self, frame_count=None):
        with self.panes[0] as v:
            with self.cameras[0] as c:
                pass
                v.clear(.5, .5, .5, 1)
                self.model.test_render()
                e = 100
                with self.context.gl:
                    triangle([0, 0, 0], [e, 0, 0], [0, e, 0])
                    triangle([0, 0, 0], [0, e, 0], [0, 0, e])
                    triangle([0, 0, 0], [e, 0, 0], [0, 0, e])
                self.model.intersect(c.frusrum_ray(*v.local_cursor()))

MyWindow().run_all(1)

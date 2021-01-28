import glfw

from doodler import *
from mkernel import Model, Tgl, Vec, Pnt
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
        glfw.set_cursor(self.glfw_window, glfw.create_standard_cursor(glfw.CROSSHAIR_CURSOR))

    def draw(self, frame_count=None):
        with self.panes[0] as v:
            with self.cameras[0] as c:
                v.clear(.5, .5, .5, 1)
                self.model.render()

                e = 100
                triangle([0, 0, 0], [e, 0, 0], [0, e, 0])
                triangle([0, 0, 0], [0, e, 0], [0, 0, e])
                triangle([0, 0, 0], [e, 0, 0], [0, 0, e])
                self.devices.mouse.cursor_goto_center()
                self.model.intersect(c.frusrum_ray(*v.local_cursor()))

                # glitch
                zoff = -50
                e = 10
                tm = c.tripod.in_plane.r.trnsf_mat
                p0 = tm * Pnt(e, 0, zoff)
                p1 = tm * Pnt(0, e, zoff)
                p2 = tm * Pnt(0, 0, zoff)
                triangle(p0.xyz, p1.xyz, p2.xyz)
                print(Vec() == 0)


MyWindow().run_all(1)

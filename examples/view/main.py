from gkernel.dtype.geometric.primitive import Pnt, Tgl
from mkernel.model import *
from wkernel import Window


# from gkernel.dtype.geometric.complex import

class W(Window):
    def __init__(self):
        super().__init__(500, 300, 'window1')

    def setup(self):
        print('setting up')
        self.framerate = 2
        self.panes.new_pane(0.25, 0.25, 0.5, 0.5)
        # self.views.new_view(0, 0, 0.5, 0.5)
        self.cameras[0].tripod.lookat((100, 100, 100), (0, 0, 0), (0, 0, 1))
        # self.cameras[0].set_fps_dolly(self)

    def draw(self):
        super().draw()

        with self.panes[1] as v:
            v.clear(0, 1, 0.5, 1)
            with self.cameras[0] as c:
                print()
                print(self.devices.mouse.cursor_in_view(v))
                print(self.cameras[0].tripod.plane.r.origin)
                print(self.cameras[0].body.PM.r * self.cameras[0].tripod.VM.r * Pnt(0, 0))
                a = 100
                model = Model()
                model.append_shape(Tgl((0, 0, 0), (a, 0, 0), (0, a, 0)))
                model.append_shape(Tgl((0, 0, 0), (-a, 0, 0), (0, -a, 0)))
                model.append_shape(Tgl((a, a, 0), (a, 0, 0), (0, a, 0)))
                self.devices.mouse.intersect_model(v, c, model)



w = W()
w.run_all()

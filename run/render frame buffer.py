from wkernel import Window
from mkernel import Model
import gkernel.dtype.geometric as gt
import glfw
import time


class MainWindow(Window):
    def __init__(self):
        super().__init__(1000, 1000, 'mywindow')
        # want to create frame
        w, h = self.glyph.size
        ffactory = self.devices.frames.factory
        ffactory.set_size(w, h)
        ffactory.append_texture(target=ffactory.TEXTURE.TARGET.TWO_D,
                                format=ffactory.TEXTURE.FORMAT.RGB)
        ffactory.set_render_buffer(format=ffactory.RENDER.DEPTH_STENCIL.D24_S8)
        ffactory.create()
        # create pane
        self.devices.panes.appendnew_pane(0, 0, 0.6, 0.6, self)

        model = Model()
        p0 = model.add_pnt(0, 0, 0)
        p0.dia = 2
        p0.clr = 1, 1, 0, 1
        p1 = model.add_pnt(10, 10, 10)
        p1.dia = 5
        p1.clr = 1, 1, 0, 1
        self.model = model
        self.is_rendered = False

    def draw(self):
        with self.devices.frames[0] as f:
            f.clear(0, 0, 0, 1)
        with self.devices.cameras[0] as c:
            with self.devices.frames[1] as off:
                off.clear(1, 0, 0, 1)
                self.model.render()
                self.is_rendered = True
            # with self.devices.panes[1] as p:
            off.render_pane_space(0, (-1, 1), (-1, 1), 0.9, (0, 1), (0, 1))


class SubWindow(Window):
    def __init__(self, mother):
        super().__init__(500, 500, 'sub window', shared=mother)
        self.ma = mother

    def draw(self):
        with self.devices.frames[0] as f:
            f.clear(1, 1, 1, 1)
            if self.ma.is_rendered:
                self.ma.devices.frames[1].render_pane_space(0, (-1, 1), (-1, 1), 0, (0, 1), (0, 1))


window_main = MainWindow()
window_sub = SubWindow(window_main)

window_main.run_all(2)

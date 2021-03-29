from wkernel import Window
from mkernel import Model
from mkernel.color_registry import GlobalColorRegistry
import gkernel.dtype.geometric as gt
import glfw
import time


class MainWindow(Window):
    def __init__(self):
        super().__init__(500, 1000, 'mywindow')
        self.framerate = 5
        # want to create frame
        w, h = self.glyph.size
        ffactory = self.devices.frames.factory
        ffactory.set_size(w, h)
        ffactory.append_texture(target=ffactory.TXTR.TRGT.TWO_D,
                                format=ffactory.TXTR.FORMAT.RGBA,
                                tid=0)
        ffactory.append_texture(target=ffactory.TXTR.TRGT.TWO_D,
                                format=ffactory.TXTR.FORMAT.RGB,
                                tid=1)
        ffactory.set_render_buffer(format=ffactory.RNDR.DEPTH_STENCIL.D24_S8,
                                   attachment_loc=None)
        ffactory.create()
        # create pane
        self.devices.panes.appendnew_pane(0.1, 0.1, 0.6, 0.6, self)

        model = Model()
        p0 = model.add_pnt(0, 0, 0)
        p0.dia = 2
        p0.clr = 1, 1, 0, 1
        p1 = model.add_pnt(10, 10, 10)
        p1.dia = 5
        p1.clr = 1, 1, 0, 1
        p1.frm = p1.FORM_CIRCLE

        p2 = model.add_pnt(20, 20, 20)
        p2.dia = 5
        p2.clr = 1, 1, 0, 1
        p2.frm = p2.FORM_TRIANGLE

        self.model = model
        self.is_rendered = False

    def draw(self):
        with self.devices.frames[0] as f:
            f.clear(0, 0, 0, 1)
            f.clear_depth()
        with self.devices.cameras[0] as c:
            if not self.is_rendered:
                with self.devices.frames[1] as f:
                    f.clear_depth()
                    f.clear_texture(0, .5, .5, .5, 1)
                    f.clear_texture(1, 0, 0, 0, 1)
                    self.model.render()
                    self.is_rendered = True

        with self.devices.panes[1] as p:
            self.devices.frames[1].render_pane_space(0, (-1, 1), (-1, 1), 0.9, (0, 1), (0, 1))
            with self.devices.frames[1] as f:
                pos = p.cursor_pos_instant(parameterize=True)
                c = f.pick_texture(tid=1, pos=pos, parameterized=True).as_byte
                e = GlobalColorRegistry().get_registered(tuple(c))
                print(e)


class SubWindow(Window):
    def __init__(self, mother):
        super().__init__(500, 500, 'sub window', shared=mother)
        self.ma = mother

    def draw(self):
        time.sleep(0.1)
        with self.devices.frames[0] as f:
            f.clear_depth()
            if self.ma.is_rendered:
                self.ma.devices.frames[1].render_pane_space(1, (-1, 1), (-1, 1), 0, (0, 1), (0, 1))


window_main = MainWindow()
window_sub = SubWindow(window_main)

window_main.run_all()

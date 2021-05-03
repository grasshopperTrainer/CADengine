from wkernel import Window
from mkernel import AModeler
from mkernel.global_id_provider import GIDP
import time

"""
picking entity by color id texture
"""


class MainWindow(Window):
    def __init__(self):
        super().__init__(500, 1000, 'mywindow')
        self.fps = 1

        # create frame
        w, h = self.glyph.size
        ffactory = self.devices.frames.factory
        ffactory.set_size(w, h)
        ffactory.append_color_texture(target=ffactory.TXTR.TRGT.TWO_D,
                                      iformat=ffactory.TXTR.CLR_FRMT.RGBA.RGBA,
                                      aid=0)
        ffactory.append_color_texture(target=ffactory.TXTR.TRGT.TWO_D,
                                      iformat=ffactory.TXTR.CLR_FRMT.RGB.RGB,
                                      aid=1)
        ffactory.append_render_buffer(iformat=ffactory.RNDR.DEPTH_STENCIL.DEPTH24_STENCIL8,
                                      aid='ds')
        ffactory.create()

        # create pane
        self.devices.panes.appendnew_pane(0.1, 0.1, 0.6, 0.6, self)

        # create model
        self.modeler = AModeler()
        self.model = self.modeler.add_model(parent=None)

        p0 = self.modeler.add_pnt(self.model, 0, 0, 0)
        p0.dia = 2
        p0.clr = 1, 1, 0, 1
        p1 = self.modeler.add_pnt(self.model, 10, 10, 10)
        p1.dia = 5
        p1.clr = 1, 1, 0, 1
        p1.frm = 'c'
        p2 = self.modeler.add_pnt(self.model, 20, 20, 20)
        p2.dia = 5
        p2.clr = 1, 1, 0, 1
        p2.frm = 't'

        self.is_rendered = False

    def draw(self):
        with self.devices.frames[0] as df:
            df.clear(0, 0, 0, 1)
            df.clear_depth()

            with self.devices.cameras[0]:
                if not self.is_rendered:
                    with self.devices.frames[1] as rf:
                        rf.clear_depth()
                        rf.clear_texture(0, .5, .5, .5, 1)
                        rf.clear_texture(1, 0, 0, 0, 1)
                        self.modeler.render()
                        self.is_rendered = True

            with self.devices.panes[1]:
                self.devices.frames[1].render_pane_space(0, (0, 1, 0, 1), (-1, 1, -1, 1), 0.9)

            with self.devices.frames[1] as rf:
                # manual pos transformation
                pos = self.devices.cursors[0].pos_global
                pos -= self.devices.panes[1].pos
                pos /= self.devices.panes[1].size
                # pick color id
                goid = rf.pick_pixels(aid=1, pos=pos, size=(1, 1))[0][0]
                if goid:
                    e = GIDP().get_registered(goid)
                    print('POINTING AT', e)


class SubWindow(Window):
    def __init__(self, mother):
        super().__init__(500, 500, 'sub window', shared=mother)
        self.ma = mother

    def draw(self):
        time.sleep(0.1)
        with self.devices.frames[0] as f:
            f.clear_depth()
            if self.ma.is_rendered:
                self.ma.devices.frames[1].render_pane_space(1, (-1, 1, -1, 1), (0, 1, 0, 1), 0)


window_main = MainWindow()
# window_sub = SubWindow(window_main)

window_main.run_all()
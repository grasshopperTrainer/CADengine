from wkernel import Window
from mkernel import AModeler
from mkernel.global_id_provider import GIDP
import gkernel.dtype.geometric as gt
import time


class MainWindow(Window):
    def __init__(self):
        super().__init__(800, 1000, 'mywindow')
        self.framerate = 60
        # want to create frame
        w, h = self.glyph.size
        ffactory = self.devices.frames.factory
        ffactory.set_size(w, h)
        ffactory.append_color_texture(target=ffactory.TXTR.TRGT.TWO_D,
                                      iformat=ffactory.TXTR.CLR_FRMT.RGBA.RGBA,
                                      aid=0)
        ffactory.append_color_texture(target=ffactory.TXTR.TRGT.TWO_D,
                                      iformat=ffactory.TXTR.CLR_FRMT.RGBA.RGB10_A2,
                                      aid=1)  # color id texture
        ffactory.append_depth_texture(target=ffactory.TXTR.TRGT.TWO_D,
                                      iformat=ffactory.TXTR.DEPTH_FRMT.DEPTH_COMPONENT)
        ffactory.create()

        # create pane
        self.devices.panes.appendnew_pane(0.1, 0.1, 0.6, 0.6, self)

        # set camera
        self.devices.cameras[0].tripod.lookat(eye=(100, 50, 30), at=(0, 0, 0), up=(0, 0, 1))
        self.devices.cameras.attach_fps_dolly(camera_id=0, cursor_id=0)

        # draw something
        self.modeler = AModeler()
        self.model = self.modeler.add_model(parent=None)
        self.modeler.add_ground(self.model, (.8, .8, .8, 1))

        for x in range(3):
            for y in range(3):
                p = self.modeler.add_pnt(self.model, x*20, y*20, 0)
                p.dia = 5
                p.clr = 1, 0, 0, 1
                p.frm = 'c'

        p1 = self.modeler.add_pnt(self.model, 12, 12, 12)
        p1.dia = 5
        p1.clr = 1, 0, 0, 1
        p1.frm = 'c'

        p2 = self.modeler.add_pnt(self.model, 10, 10, 10)
        p2.dia = 5
        p2.clr = 1, 1, 0, 1
        p2.frm = 't'

        p3 = self.modeler.add_pnt(self.model, 80, 30, 0)
        p3.dia = 5
        p3.clr = 1, 1, 1, 1
        p3.frm = 't'

        self._ref_pnts = []
        for _ in range(4):
            pnt = self.modeler.add_pnt(self.model, 0, 0, 0)
            pnt.dia = 0.05
            self._ref_pnts.append(pnt)

        self.is_rendered = False

    def draw(self):
        with self.devices.frames[0] as deff:
            deff.clear(0, 0, 0, 1)
            deff.clear_depth()
        with self.devices.cameras[0] as cam:
            for pnt, (dx, dy) in zip(self._ref_pnts, ((1, 1), (-1, -1), (1, -1), (-1, 1))):
                a = 0.1
                x, y = dx*a, dy*a
                pnt.geo = cam.tripod.plane.TM * gt.Pnt(x, y, -10)

            with self.devices.frames[1] as f:
                f.clear_depth()
                f.clear_texture(0, .5, .5, .5, 1)
                f.clear_texture(1, 0, 0, 0, 1)
                self.modeler.render()
                self.is_rendered = True

        with self.devices.panes[1] as p:
            self.devices.frames[1].render_pane_space_depth(0, (0, 1, 0, 1), (-1, 1, -1, 1))
            with self.devices.frames[1] as deff:
                # pos = p.cursor_pos(parameterize=True)
                goid, bitpattern = deff.pick_pixels(aid=1, pos=(.5, .5), size=(1, 1))
                goid = goid[0][0]
                e = GIDP().get_registered_byvalue(goid, bitpattern)
                if e:
                    print(goid, e)


class SubWindow(Window):
    def __init__(self, mother):
        super().__init__(500, 500, 'sub window', shared=mother)
        self.framerate = 5
        self.ma = mother

        self.devices.panes.appendnew_pane(0, 0, 0.5, 0.5, self)
        self.devices.panes.appendnew_pane(0.5, 0, 0.5, 0.5, self)
        self.devices.panes.appendnew_pane(0.5, 0.5, 0.5, 0.5, self)

    def draw(self):
        time.sleep(0.1)
        with self.devices.frames[0] as f:
            f.clear()
            f.clear_depth()
            with self.devices.panes[1]:
                self.ma.devices.frames[1].render_pane_space(0, (0, 1, 0, 1), (-1, 1, -1, 1), 0)
            with self.devices.panes[2]:
                self.ma.devices.frames[1].render_pane_space(1, (0, 1, 0, 1), (-1, 1, -1, 1), 0)
            with self.devices.panes[3]:
                    self.ma.devices.frames[1].render_pane_space('d', (0, 1, 0, 1), (-1, 1, -1, 1), 0)

window_main = MainWindow()
window_sub = SubWindow(window_main)

window_main.run_all()

from wkernel import Window
from mkernel import AModeler


class MyWindow(Window):
    def __init__(self):
        super().__init__(500, 800, 'mywindow', None, None)
        self.fps = 5
        # set camera
        camera = self.devices.cameras[0]
        camera.tripod.lookat(eye=(100, 100, 100),
                             at=(0, 0, 0),
                             up=(0, 0, 1))
        # set frame
        ff = self.devices.frames.factory
        ff.append_color_texture(ff.TXTR.TRGT.TWO_D, ff.TXTR.CLR_FRMT.RGBA.RGBA, aid=0)  # color
        ff.append_color_texture(ff.TXTR.TRGT.TWO_D, ff.TXTR.CLR_FRMT.RGBA.RGBA, aid=1)  # id
        ff.append_color_texture(ff.TXTR.TRGT.TWO_D, ff.TXTR.CLR_FRMT.RGB.RGB32F, aid=2)  # coordinate
        ff.append_depth_texture(ff.TXTR.TRGT.TWO_D, ff.TXTR.DEPTH_FRMT.DEPTH_COMPONENT)  # depth
        ff.set_size(*self.glyph.size)
        ff.create()

        # set model
        self.modeler = AModeler()
        self.model = self.modeler.add_model(parent=None)
        self.modeler.add_ground(self.model, (.5, .5, .5, 1))
        self.modeler.add_pnt(self.model, 0, 0, 0)
        t = self.modeler.add_tgl(self.model, (10, 0, 5), (0, 10, 5), (0, 0, 5))
        t.clr_edge = 1, 0, 0, 1
        t.edge_thk = 5
        l = self.modeler.add_lin(self.model, (10, 0, 10), (0, -100, 0))
        l.clr = 1, 0, 1, 1

        pl = self.modeler.add_plin(self.model, [0, 0, 0], [-5, 0, 10], [10, 0, 50])
        pl.clr = 1, 1, 1, 1

        self.modeler.add_pln(self.model, (0, 0, 0.001), (1, 0, 0), (0, 1, 0), (0, 0, 1))

        a = 10
        for x in range(10):
            for y in range(10):
                for z in range(1):
                    p = self.modeler.add_pnt(self.model, a * x, a * y, a * z)
                    p.frm = 'c'
                    p.dia = 3
                    if z % 2 == 0:
                        p.frm = 't'
                    if (x + y + z) % 2 == 0:
                        p.frm = 's'

    def draw(self):
        with self.devices.frames[0] as df:
            df.clear(0, 0, 0, 1)
            df.clear_depth()

            with self.devices.cameras[0] as c:
                with self.devices.frames[1] as df:
                    df.clear(0, 0, 0, 1)
                    df.clear_depth()
                    self.modeler.render()

                    coord, _ = df.pick_pixels(2, self.devices.cursors[0].pos_global.astype(int), size=(1, 1))
                    print(coord[0][0])

        df.render_pane_space_depth(aid=0)


class SubWindow(Window):
    def __init__(self, mother):
        super().__init__(500, 500, 'sub window', shared=mother)
        self.framerate = 5
        self.ma = mother

        self.devices.panes.appendnew_pane(0, 0, 0.5, 0.5, self)
        self.devices.panes.appendnew_pane(0.5, 0, 0.5, 0.5, self)
        self.devices.panes.appendnew_pane(0.5, 0.5, 0.5, 0.5, self)
        self.devices.panes.appendnew_pane(0, 0.5, 0.5, 0.5, self)

    def draw(self):
        with self.devices.frames[0] as f:
            f.clear_depth()
            mf = self.ma.devices.frames[1]
            with self.devices.panes[1]:
                mf.render_pane_space(0, (0, 1, 0, 1), (-1, 1, -1, 1), 0)
            with self.devices.panes[2]:
                mf.render_pane_space(1, (0, 1, 0, 1), (-1, 1, -1, 1), 0)
            with self.devices.panes[3]:
                mf.render_pane_space(2, (0, 1, 0, 1), (-1, 1, -1, 1))
            with self.devices.panes[4]:
                mf.render_pane_space('d', (0, 1, 0, 1), (-1, 1, -1, 1), 0)


window_main = MyWindow()
window_sub = SubWindow(window_main)

window_main.run_all()

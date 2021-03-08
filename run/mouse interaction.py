from wkernel import Window
from mkernel import Model


class MyWindow(Window):
    def __init__(self):
        super(MyWindow, self).__init__(500, 880, 'mywindow', None, None)
        self.framerate = 30

        self.devices.cameras[0].tripod.lookat(eye=(100, 50, 100),
                                              at=(0, 0, 0),
                                              up=(0, 0, 1))

        # creeat frame
        ff = self.devices.frames.factory
        ff.append_color_texture(ff.TXTR.TRGT.TWO_D, ff.TXTR.CLR_FRMT.RGBA.RGBA, loc=0)
        ff.append_color_texture(ff.TXTR.TRGT.TWO_D, ff.TXTR.CLR_FRMT.RGB.RGB, loc=1)
        ff.append_color_texture(ff.TXTR.TRGT.TWO_D, ff.TXTR.CLR_FRMT.RGBA.RGBA32F, loc=2)
        ff.append_depth_texture(ff.TXTR.TRGT.TWO_D, ff.TXTR.DEPTH_FRMT.DEPTH_COMPONENT)
        ff.set_size(500, 880)
        ff.create()

        # attach dolly
        self.cad_dolly = self.devices.cameras.attach_cad_dolly(camera_id=0, cursor_id=0)

        self.model = Model()
        self.model.add_pln((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))

        a = 10
        for x in range(10):
            for y in range(10):
                self.model.add_pnt(x * a, y * a, a)

    def draw(self):
        with self.devices.frames[0] as f:
            f.clear(0, 0, 0, 0)
            f.clear_depth()

            with self.devices.frames[1] as f:
                f.clear(0, 0, 0, 0)
                f.clear_depth()
                self.model.render()
                v = f.pick_texture(tid=2, pos=self.devices.cursors[0].pos_local, parameterized=False)
                self.cad_dolly.set_orbit_origin(*v.rgb)
            f.render_pane_space_depth(tid=0)


class DebuggerWindow(Window):
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
            f.clear()
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


mw = MyWindow()
sw = DebuggerWindow(mw)
mw.run_all()

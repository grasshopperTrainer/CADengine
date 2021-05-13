from wkernel import Window
from mkernel import AModeler, AController


class MyWindow(Window):
    def __init__(self):
        super(MyWindow, self).__init__(500, 880, 'mywindow', None, None)
        self.fps = 30

        self.devices.cameras[0].tripod.lookat(eye=(100, 50, 100),
                                              at=(0, 0, 0),
                                              up=(0, 0, 1))
        # creeat frame
        ff = self.devices.frames.factory
        ff.append_color_texture(ff.TXTR.TRGT.TWO_D, ff.TXTR.CLR_FRMT.RGBA.RGBA, aid=0)
        ff.append_color_texture(ff.TXTR.TRGT.TWO_D, ff.TXTR.CLR_FRMT.RGBA.RGB10_A2, aid=1, name='goid')
        ff.append_color_texture(ff.TXTR.TRGT.TWO_D, ff.TXTR.CLR_FRMT.RGBA.RGBA32F, aid=2, name='coord')
        ff.append_depth_texture(ff.TXTR.TRGT.TWO_D, ff.TXTR.DEPTH_FRMT.DEPTH_COMPONENT)
        ff.set_size(500, 880)
        ff.create()

        # attach dolly
        self.cad_dolly = self.devices.cameras.attach_cad_dolly(camera_id=0, cursor_id=0, def_offset=500)

        self.modeler = AModeler()
        self.model = self.modeler.add_model(parent=None)
        self.modeler.add_ground(self.model, (.5, .5, .5, .5))
        self.modeler.add_pln(self.model, (0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))


        self.id_picker = self.devices.frames[1].create_pixel_picker(aid=1)
        self.coord_picker = self.devices.frames[1].create_pixel_picker(aid=2)
        self.controller = AController(self,
                                      self.modeler,
                                      self.model,
                                      self.id_picker,
                                      self.coord_picker,
                                      self.devices.cameras[0],
                                      self.devices.cursors[0])

        print("Press 'd' to remove selected point")

    def draw(self):
        with self.devices.frames[0] as rf:
            rf.clear(0, 0, 0, 0)
            rf.clear_depth()

            with self.devices.frames[1] as df:
                df.clear(0, 0, 0, 0)
                df.clear_depth()
                self.modeler.render()

                # update camera move
                # extract coordinate texture value
                txtr_pos = self.devices.cursors[0].pos_local * self.devices.frames[1].size
                coord, _ = self.coord_picker.pick(pos=txtr_pos.astype(int), size=(1, 1))
                coord = coord[0][0].tolist()[:3]
                if coord != [0, 0, 0]:
                    self.cad_dolly.set_ref_point(*coord)

            df.render_pane_space_depth(aid=0)


class DebuggerWindow(Window):
    def __init__(self, mother):
        super().__init__(500, 500, 'sub window', shared=mother)
        self.framerate = 60
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


if __name__ == '__main__':
    mw = MyWindow()
    sw = DebuggerWindow(mw)
    mw.run_all()

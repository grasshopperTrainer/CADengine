from mkernel import AModel, BModeler
from wkernel import Window
import gkernel.color as clr
import gkernel.dtype.geometric as gt


class MyWindow(Window):
    def __init__(self):
        super().__init__(800, 1000, 'my window 1', monitor=None, shared=None)
        self.fps = 30
        self.cad_dolly = self.devices.cameras.attach_cad_dolly(0, 0, 500)
        self.devices.cameras[0].tripod.lookat((0, 0, 100), (0, 0, 0), (0, 1, 0))

        # draw frame
        ff = self.devices.frames.factory
        ff.append_color_texture(target=ff.TXTR.TRGT.TWO_D,
                                iformat=ff.TXTR.CLR_FRMT.RGBA.RGBA,
                                aid=0,
                                name='albedo')
        ff.append_color_texture(target=ff.TXTR.TRGT.TWO_D,
                                iformat=ff.TXTR.CLR_FRMT.RGB.RGB,
                                aid=1,
                                name='id')
        ff.append_color_texture(target=ff.TXTR.TRGT.TWO_D,
                                iformat=ff.TXTR.CLR_FRMT.RGBA.RGBA32F,
                                aid=2,
                                name='coord')
        ff.append_depth_texture(target=ff.TXTR.TRGT.TWO_D,
                                iformat=ff.TXTR.DEPTH_FRMT.DEPTH_COMPONENT,
                                name='depth')
        ff.set_size(*self.glyph.size)
        draw_frame = ff.create()

        self.coord_picker = draw_frame.create_pixel_picker('coord')
        self.id_picker = draw_frame.create_pixel_picker('id')

        # create model
        model = AModel()
        self.model = model
        self.model.add_ground((.3, .3, .3, .3))
        self.model.add_pln((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))

        self.modeler = BModeler(self.model.add_brep())
        # b = self.model.add_brep()  # set root?

    def draw(self, frame_count=None):
        # update cam
        coord = self.coord_picker.pick(pos=self.devices.cursors[0].pos_global.astype(int), size=(1, 1))
        coord = clr.ClrRGBA(*coord[0][0]).rgb
        self.cad_dolly.set_ref_point(*coord)

        # do modeling
        self.modeler.listen(self.model,
                            self,
                            self.devices.mouse,
                            self.devices.cameras[0],
                            self.devices.cursors[0],
                            self.id_picker,
                            self.coord_picker)

        # draw on draw frame
        with self.devices.frames[1] as df:
            with self.devices.cameras[0]:
                with self.devices.panes[0]:
                    df.clear_texture(1, 0, 0, 0, 1)
                    df.clear(0, 0, 0, 1)
                    df.clear_depth()
                    self.model.render()

        # draw on render frame
        with self.devices.frames[0] as rf:
            rf.clear()
            rf.clear_depth()
            df.render_pane_space_depth(aid=0, txtr_domain=(0, 1, 0, 1), pane_domain=(-1, 1, -1, 1))


class DebuggerWindow(Window):
    def __init__(self, mother):
        super().__init__(400, 1000, 'sub window', shared=mother)
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

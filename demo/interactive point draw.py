from wkernel import Window
from mkernel import Model, AModeler
from skernel.environmental.ground import Ground
import gkernel.color as clr
import time


class MyWindow(Window):
    def __init__(self):
        super(MyWindow, self).__init__(500, 880, 'mywindow', None, None)
        self.framerate = 30

        self.devices.cameras[0].tripod.lookat(eye=(100, 50, 100),
                                              at=(0, 0, 0),
                                              up=(0, 0, 1))
        # creeat frame
        ff = self.devices.frames.factory
        ff.append_color_texture(ff.TXTR.TRGT.TWO_D, ff.TXTR.CLR_FRMT.RGBA.RGBA, aid=0)
        ff.append_color_texture(ff.TXTR.TRGT.TWO_D, ff.TXTR.CLR_FRMT.RGB.RGB, aid=1, name='cid')
        ff.append_color_texture(ff.TXTR.TRGT.TWO_D, ff.TXTR.CLR_FRMT.RGBA.RGBA32F, aid=2, name='coord')
        ff.append_depth_texture(ff.TXTR.TRGT.TWO_D, ff.TXTR.DEPTH_FRMT.DEPTH_COMPONENT)
        ff.set_size(500, 880)
        ff.create()

        # attach dolly
        self.cad_dolly = self.devices.cameras.attach_cad_dolly(camera_id=0, cursor_id=0, def_offset=500)

        # ground
        self.ground = Ground(clr.ClrRGBA(0.5, 0.5, 0.5, 0.5))

        self.modeler = AModeler()
        self.model = Model()
        self.model.add_pln((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))

        self.count = 0
        self.t = None

        self.__id_picker = self.devices.frames[1].create_pixel_picker(aid=1)
        self.__coord_picker = self.devices.frames[1].create_pixel_picker(aid=2)

    def draw(self):
        self.count += 1
        with self.devices.frames[0] as f:
            f.clear(0, 0, 0, 0)
            f.clear_depth()

            with self.devices.frames[1] as f:
                self.modeler.listen(self.model,
                                    self,
                                    self.devices.mouse,
                                    self.devices.keyboard,
                                    self.devices.cameras[0],
                                    self.devices.cursors[0],
                                    self.__id_picker)

                # draw ground and model
                f.clear(0, 0, 0, 0)
                f.clear_depth()
                self.ground.render(self.devices.cameras[0])
                self.model.render()

                # update camera move
                # extract coordinate texture value
                txtr_pos = self.devices.cursors[0].pos_local * self.devices.frames[1].size
                v = self.__coord_picker.pick(pos=txtr_pos.astype(int), size=(1, 1))
                coord = clr.ClrRGBA(*v[0][0]).rgb
                if coord != (0, 0, 0):
                    self.cad_dolly.set_ref_point(*coord)

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


if __name__ == '__main__':
    mw = MyWindow()
    sw = DebuggerWindow(mw)
    mw.run_all()

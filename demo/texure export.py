from wkernel import Window
from mkernel import Model
import gkernel.color as clr
import gkernel.dtype.geometric as gt
from akernel.environmental.ground import Ground
import time


if __name__ == '__main__':

    class MainWindow(Window):
        def __init__(self):
            super().__init__(500, 800, 'mywindow')
            self.framerate = 60
            # want to create frame
            w, h = self.glyph.size
            ffactory = self.devices.frames.factory
            ffactory.set_size(w, h)
            ffactory.append_color_texture(target=ffactory.TXTR.TRGT.TWO_D,
                                          format=ffactory.TXTR.CLR_FRMT.RGBA.RGBA,
                                          lid=0)
            ffactory.append_color_texture(target=ffactory.TXTR.TRGT.TWO_D,
                                          format=ffactory.TXTR.CLR_FRMT.RGB.RGB,
                                          lid=1)  # color id texture
            ffactory.append_depth_texture(target=ffactory.TXTR.TRGT.TWO_D,
                                          format=ffactory.TXTR.DEPTH_FRMT.DEPTH_COMPONENT)
            ffactory.create()

            # create pane
            self.devices.panes.appendnew_pane(0.1, 0.1, 0.6, 0.6, self)

            # set camera
            self.devices.cameras[0].tripod.lookat(eye=(100, 50, 30), at=(0, 0, 0), up=(0, 0, 1))

            self.devices.cameras.attach_fps_dolly(camera_id=0, cursor_id=0)

            # draw something
            model = Model()

            for x in range(3):
                for y in range(3):
                    p = model.add_pnt(x*20, y*20, 0)
                    p.dia = 5
                    p.clr = 1, 0, 0, 1
                    p.frm = p.FORM_CIRCLE

            p1 = model.add_pnt(12, 12, 12)
            p1.dia = 5
            p1.clr = 1, 0, 0, 1
            p1.frm = p1.FORM_CIRCLE

            p2 = model.add_pnt(10, 10, 10)
            p2.dia = 5
            p2.clr = 1, 1, 0, 1
            p2.frm = p2.FORM_TRIANGLE

            p3 = model.add_pnt(80, 30, 0)
            p3.dia = 5
            p3.clr = 1, 1, 1, 1
            p3.frm = p3.FORM_TRIANGLE

            self.ref0 = model.add_pnt(0, 0, 0)
            self.ref1 = model.add_pnt(0, 0, 0)
            self.ref2 = model.add_pnt(0, 0, 0)

            self.ref0.dia = 0.5
            self.ref1.dia = 0.5
            self.ref2.dia = 0.5
            self.ref1.frm = p1.FORM_TRIANGLE

            self.model = model
            self.ground = Ground(clr.ClrRGBA(.8, .8, .8, 1))
            self.count = 0

            print('press "1" to export current scene')

        def draw(self):
            # clean default frame
            with self.devices.frames[0] as deff:
                deff.clear(0, 0, 0, 1)
                deff.clear_depth()

            # draw on draw frame
            with self.devices.frames[1] as f:
                f.clear_depth()
                f.clear_texture(0, .5, .5, .5, 1)
                f.clear_texture(1, 0, 0, 0, 1)
                self.model.render()

            with self.devices.panes[1]:
                self.ground.render(self.devices.cameras[0])
                self.devices.frames[1].render_pane_space_depth(0, (0, 1, 0, 1), (-1, 1, -1, 1))
                if self.devices.keyboard.get_key_status('1'):
                    self.devices.frames[1].frame_bffr.textures[0].image_export(f"{self.count}.jpg")
                    self.count += 1


    class SubWindow(Window):
        def __init__(self, mother):
            super().__init__(500, 500, 'sub window', shared=mother)
            self.framerate = 60
            self.ma = mother

            self.devices.panes.appendnew_pane(0, 0, 0.5, 0.5, self)
            self.devices.panes.appendnew_pane(0.5, 0, 0.5, 0.5, self)
            self.devices.panes.appendnew_pane(0.5, 0.5, 0.5, 0.5, self)

        def draw(self):
            time.sleep(0.1)
            with self.devices.frames[0] as f:
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

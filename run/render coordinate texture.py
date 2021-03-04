from wkernel import Window
from mkernel import Model
from akernel.environmental.ground import Ground
from akernel.picker import InitPosPicker


class MyWindow(Window):
    def __init__(self):
        super().__init__(500, 800, 'mywindow', None, None)
        self.framerate = 120
        # set camera
        camera = self.devices.cameras[0]
        camera.tripod.lookat(eye=(-100, -100, 100),
                             at=(0, 0, 0),
                             up=(0, 0, 1))
        # set frame
        ff = self.devices.frames.factory
        ff.append_color_texture(ff.TEXTURE.TARGET.TWO_D, ff.TEXTURE.FORMAT.RGBA, loc=0)  # color
        ff.append_color_texture(ff.TEXTURE.TARGET.TWO_D, ff.TEXTURE.FORMAT.RGBA, loc=1)  # id
        ff.append_color_texture(ff.TEXTURE.TARGET.TWO_D, ff.TEXTURE.FORMAT.DEPTH_COMPONENT, loc=2)  # depth
        ff.append_color_texture(ff.TEXTURE.TARGET.TWO_D, ff.TEXTURE.FORMAT.RGB10_A2, loc=3)  # coordinate
        ff.create()

        # set model
        self.model = Model()
        self.model.add_pln((0, 0, 0.001), (1, 0, 0), (0, 1, 0), (0, 0, 1))
        # self.model.add_pln((10, 23, 10), (6, 4, 24), (5, 6, 10), (2, 100, 1))
        # self.model.add_pnt(0, 0, 0)
        self.ground = Ground([.5] * 4)

    def draw(self):
        with self.devices.frames[0] as df:
            df.clear(0, 0, 0, 1)
            df.clear_depth()

            with self.devices.cameras[0] as c:
                with self.devices.frames[1] as df:
                    self.ground.render(c)
                    self.model.render()

        # with self.devices.panes[0] as p:
        #     p.

class SubWindow(Window):
    def __init__(self, mother):
        super().__init__(500, 500, 'sub window', shared=mother)
        self.framerate = 5
        self.ma = mother

        self.devices.panes.appendnew_pane(0, 0, 0.5, 0.5, self)
        self.devices.panes.appendnew_pane(0.5, 0, 0.5, 0.5, self)
        self.devices.panes.appendnew_pane(0.5, 0.5, 0.5, 0.5, self)

    def draw(self):
        with self.devices.frames[0] as f:
            f.clear_depth()
            with self.devices.panes[1]:
                self.ma.devices.frames[1].render_pane_space(0, (0, 1, 0, 1), (-1, 1, -1, 1), 0)
            with self.devices.panes[2]:
                self.ma.devices.frames[1].render_pane_space(1, (0, 1, 0, 1), (-1, 1, -1, 1), 0)
            with self.devices.panes[3]:
                self.ma.devices.frames[1].render_pane_space('d', (0, 1, 0, 1), (-1, 1, -1, 1), 0)


window_main = MyWindow()
window_sub = SubWindow(window_main)

window_main.run_all()

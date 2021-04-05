from mkernel import Model, BModeler
from wkernel import Window
from mkernel.shapes.ground import Ground

import gkernel.color as clr


class MyWindow(Window):
    def __init__(self):
        super().__init__(1000, 1200, 'my window 1', monitor=None, shared=None)
        self.fps = 120
        self.cad_dolly = self.devices.cameras.attach_cad_dolly(0, 0, 500)

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
        ff.set_size(1000, 1200)
        draw_frame = ff.create()

        self.coord_picker = draw_frame.create_pixel_picker('coord')
        self.id_picker = draw_frame.create_pixel_picker('id')

        # create model
        model = Model()
        self.model = model
        self.model.add_pln((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
        self.model.add_ground((.3, .3, .3, .3))
        b = self.model.add_brep()  # set root?

        self.modeler = BModeler(b)

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
                            self.id_picker)

        # draw on draw frame
        with self.devices.frames[1] as df:
            with self.devices.cameras[0] as cam:
                with self.devices.panes[0] as pane:
                    df.clear(.5, .5, .5, 1)
                    df.clear_depth()
                    self.model.render()

        # draw on render frame
        with self.devices.frames[0] as rf:
            rf.clear()
            rf.clear_depth()
            df.render_pane_space_depth(aid=0, txtr_domain=(0, 1, 0, 1), pane_domain=(-1, 1, -1, 1))


MyWindow().run_all()

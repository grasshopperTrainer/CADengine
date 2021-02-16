from wkernel import Window


class MyWindow(Window):
    def __init__(self):
        super().__init__(100, 100, 'mywindow')
        # want to create frame
        w, h = self.glyph.size
        ffactory = self.devices.frames.factory
        ffactory.append_texture(target=ffactory.TEXTURE.TARGET.TWO_D,
                                format=ffactory.TEXTURE.FORMAT.RGB,
                                width=w,
                                height=h)
        ffactory.set_render_buffer(format=ffactory.RENDER.DEPTH_STENCIL.D24_S8,
                                   width=w,
                                   height=h)
        ffactory.create()

    def draw(self):
        with self.devices.frames[0] as frame:
            print(frame)


MyWindow().run_all(1)

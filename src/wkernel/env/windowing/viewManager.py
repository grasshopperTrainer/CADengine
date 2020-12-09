from .window_properties import *
from .glyph import GlyphNode
from wkernel.hooked import openglHooked as gl


class View(RenderTarget):
    def __init__(self, x_exp, y_exp, w_exp, h_exp, par_x, par_y, par_w, par_h, par_m, pool):
        super().__init__(pool)

        self._glyph = GlyphNode(x_exp, y_exp, w_exp, h_exp, par_x, par_y, par_w, par_h, par_m)

    def __enter__(self):
        """
        Open view
        :return:
        """
        gl.glScissor(self._glyph.posx.r, self._glyph.posy.r, self._glyph.width.r, self._glyph.height.r)
        gl.glViewport(self._glyph.posx.r, self._glyph.posy.r, self._glyph.width.r, self._glyph.height.r)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Close view
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        return

    def clear(self, r=0, g=0, b=0, a=0):
        gl.glClearColor(r, g, b, a)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    def rel_mouse_pos(self):
        pass

    @property
    def glyph(self):
        return self._glyph


class ViewManager(RenderTargetManager):
    def __init__(self, window):
        super().__init__(window)
        self._append_new_target(View(0,
                                     0,
                                     1.0,
                                     1.0,
                                     window._glyph.posx,
                                     window._glyph.posy,
                                     window._glyph.width,
                                     window._glyph.height,
                                     window._glyph.trnsf_matrix,
                                     self))

    def __getitem__(self, item) -> View:
        return self._targets[item]

    def new_view(self, x_exp, y_exp, w_exp, h_exp):
        """
        Appendd new view into view pool.

        :param x_exp: expression for origin coordinate x
        :param y_exp: expression for origin coordinate y
        :param w_exp: expression for origin coordinate w
        :param h_exp: expression for origin coordinate h
        :return:
        """
        self._append_new_target(View(x_exp,
                                     y_exp,
                                     w_exp,
                                     h_exp,
                                     self.window.glyph.posx,
                                     self.window.glyph.posy,
                                     self.window.glyph.width,
                                     self.window.glyph.height,
                                     self.window.glyph.trnsf_matrix,
                                     self))

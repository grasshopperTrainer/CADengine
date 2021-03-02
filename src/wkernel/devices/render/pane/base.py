from gkernel.dtype.geometric.primitive import Pnt
from gkernel.dtype.nongeometric.matrix.primitive import ScaleMat

from wkernel.glyph import GlyphNode, GlyphInterface
from wkernel.devices.render._base import RenderDevice, RenderDeviceManager
from global_tools.lazy import lazyProp

from .cursor import Cursor


class Pane(RenderDevice, GlyphInterface):
    """
    Defines area of window to render on.

    Pane is a sheet of glass that together forms window plane
    """

    def __init__(self, x_exp, y_exp, w_exp, h_exp, parent: GlyphInterface, manager):
        """
        new pane is presented in relation with parent Pane

        expressions can be one of three and all should yield measurement in pixels:
        1. integer -> fixed pixel value
        2. float   -> value proportional to parent width or height
        3. callable  -> value derived from input of parent width or height

        :param x_exp: x pos expression
        :param y_exp: y pos expression
        :param w_exp: w pos expression
        :param h_exp: h pos expression
        :param parent : parent object implementing GlyphInterface
        :param manager: pane manager
        """
        super().__init__(manager)

        self._glyph = GlyphNode(x_exp,
                                y_exp,
                                w_exp,
                                h_exp,
                                parent.glyph.posx.r,
                                parent.glyph.posy.r,
                                parent.glyph.width.r,
                                parent.glyph.height.r)

    def __enter__(self):
        """
        Open view
        :return:
        """
        super().__enter__()  # <- must for putting in binding stack
        with self.manager.window.context.gl as gl:
            gl.glScissor(self._glyph.posx.r, self._glyph.posy.r, self._glyph.width.r, self._glyph.height.r)
            gl.glViewport(self._glyph.posx.r, self._glyph.posy.r, self._glyph.width.r, self._glyph.height.r)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        return scissor and viewport

        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        super().__exit__(exc_type, exc_val, exc_tb)
        if self.get_current() is not self:  # if self, there is no need
            glyph = self.get_current().glyph
            with self.manager.window.context.gl as gl:
                gl.glScissor(glyph.posx.r, glyph.posy.r, glyph.width.r, glyph.height.r)
                gl.glViewport(glyph.posx.r, glyph.posy.r, glyph.width.r, glyph.height.r)

    @property
    def glyph(self):
        return self._glyph

    @property
    def size(self):
        return self._glyph.size

    @property
    def pos(self):
        return self._glyph.posx.r, self._glyph.posy.r

    def clear(self, r=0, g=0, b=0, a=0):
        """
        fill with given color

        all inputs in domain(0, 1)
        :param r: red
        :param g: green
        :param b: blue
        :param a: alpha
        :return:
        """
        with self.manager.window.context.gl as gl:
            gl.glClearColor(r, g, b, a)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            gl.glClear(gl.GL_DEPTH_BUFFER_BIT)


class PaneManager(RenderDeviceManager):
    """
    Manages multitue of `Pane`

    implements global functionalities among Pane
    """

    def __init__(self, device_master):
        super().__init__(device_master)
        # default device
        p = self.appendnew_pane(x_exp=0,
                                y_exp=0,
                                w_exp=1.,
                                h_exp=1.,
                                parent=device_master.window)
        # to make it default
        self.master.tracker.stack.set_base_entity(p)

    @property
    def device_type(self):
        return Pane

    def appendnew_pane(self, x_exp, y_exp, w_exp, h_exp, parent: GlyphInterface):
        """
        Appendd new view into view pool.

        :param x_exp: expression for origin coordinate x
        :param y_exp: expression for origin coordinate y
        :param w_exp: expression for origin coordinate w
        :param h_exp: expression for origin coordinate h
        :param parent: parent implementing GlyphInterface
        :return:
        """
        pane = Pane(x_exp,
                    y_exp,
                    w_exp,
                    h_exp,
                    parent=parent,
                    manager=self)
        self._appendnew_device(pane)
        return pane

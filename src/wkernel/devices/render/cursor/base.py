import os
import numpy as np

import gkernel.dtype.geometric as gt
import ckernel.render_context.opengl_context.meta_entities as meta
import OpenGL.GL as gl

from wkernel.devices.render._base import RenderDevice, RenderDeviceManager


class _CursorRenderer:
    __path = os.path.dirname(__file__)

    __dot_prgrm = meta.MetaPrgrm(vrtx_path=os.path.join(__path, 'dot_vrtx_shdr.glsl'),
                                 frgm_path=os.path.join(__path, 'dot_frgm_shdr.glsl'))

    def __init__(self):
        self.__dot_vbo = self.__dot_prgrm.vrtxattr_schema.create_vrtx_bffr()
        self.__dot_vao = meta.MetaVrtxArry(self.__dot_vbo)

        self.__block = self.__dot_vbo.cache.request_block(size=1)

        self.__flag_push = True

        self.__pos = None
        self.__clr = None
        self.__dim = None

        self.set_pos(0, 0)
        self.set_clr(1, 1, 1, 1)
        self.set_dim(5)

    def set_pos(self, x, y):
        self.__pos = x, y
        self.__block['pos'] = x, y
        self.__flag_push = True

    def set_clr(self, r, g, b, a):
        self.__clr = r, g, b, a
        self.__block['clr'] = r, g, b, a
        self.__flag_push = True

    def set_dim(self, v):
        self.__dim = v
        self.__block['dim'] = v
        self.__flag_push = True

    def render_dot(self):
        if self.__flag_push:
            self.__dot_vbo.push_cache()
        self.__flag_push = False

        with self.__dot_prgrm:
            with self.__dot_vao:
                gl.glDrawArrays(gl.GL_POINTS, 0, 1)


class Cursor(RenderDevice):
    """
    Defines area of window to render on.

    Pane is a sheet of glass that together forms window plane
    """

    def __init__(self, origin: (tuple, list), manager):
        """

        :param origin: (x, y), cursor origin in window space
        :param manager:
        """
        super().__init__(manager)

        if not(isinstance(origin, (tuple, list)) and len(origin) == 2):
            raise TypeError
        self.__origin = gt.Vec(origin[0], origin[1])

        self.__pos_local = gt.Vec(-origin[0], -origin[1])
        self.__pos_prev = gt.Vec(0, 0, 0)
        self.__accel = gt.Vec(0, 0, 0)

        self.__renderer = _CursorRenderer()
        self.set_cursor_pos_callback(self.__default_cursor_pos_callbacked)

    def __update_pos_local(self, new_pos):
        """
        update internal acceleration
        :param new_pos:
        :return:
        """
        self.__accel = new_pos - self.__pos_local
        self.__pos_local = new_pos - self.__origin

    def __update_pos_global(self, new_pos):
        new_local = new_pos + self.__origin
        self.__update_pos_local(new_local)

    @property
    def pos_local(self):
        return self.__pos_local.xy

    @pos_local.setter
    def pos_local(self, v):
        if not (isinstance(v, (tuple, list, np.ndarray)) and len(v) == 2):
            raise ValueError('given is not position like')
        self.__update_pos_local(gt.Vec(*v))

    @property
    def pos_global(self):
        return (self.__pos_local + self.__origin).xy

    @pos_global.setter
    def pos_global(self, v):
        if not (isinstance(v, (tuple, list, np.ndarray)) and len(v) == 2):
            raise ValueError('given is not position like')
        self.__update_pos_global(gt.Vec(*v))

    @property
    def accel(self):
        return self.__accel

    def set_pos_curr(self, x, y):
        """
        set current cursor pos

        :param x:
        :param y:
        :return:
        """
        self.__pos_local = x, y

    def set_pos_prev(self, x, y):
        """
        set previous cursor pos

        this effects acceleration
        :param x:
        :param y:
        :return:
        """
        self.__pos_prev = x, y

    def set_origin(self, x, y):
        raise NotImplementedError

    def render(self):
        """
        currently dot default

        :return:
        """
        p = self.__pos_local + self.__origin
        # just simple transformation...
        param = p[:2, 0]/np.array(self.manager.window.glyph.size) * 2 - 1
        self.__renderer.set_pos(*param)
        self.__renderer.render_dot()

    def __default_cursor_pos_callbacked(self, glfww, xpos, ypos, mouse, cursor):
        """
        default cursor pos callback

        one willing to implement custom callback should refer the these argument:
        :param glfww: glfw window
        :param xpos: int, x coordinate provided by glfw
        :param ypos: int, y coordinate provided by glfw
        :param mouse: mouse device
        :param cursor: this cursor
        :return:
        """
        pos = mouse.cursor_pos_instant
        self.__update_pos_local(pos)

    def __default_cursor_enter_callbacked(self, glfww, mouse):
        pass

    def __default_cursor_exit_callbacked(self, glfww):
        raise NotImplementedError

    def __callbacked_wrapper(self, __func):
        """
        wrapper for enforcing position return
        and making acceleration atomic property

        :param __func:
        :return:
        """
        def __wrapper(*args, **kwargs):
            r = __func(*args, **kwargs)
            if not (isinstance(r, (tuple, list, np.ndarray)) and len(r) == 2):
                raise ValueError
            pos = gt.Vec(*r)
            self.__update_pos_local(pos)
        return __wrapper

    def set_cursor_pos_callback(self, func, *args, **kwargs):
        """
        for max flexibility providing raw behaviour set function

        e.g. def f(glfww, x, y, m, c): c.pos = (x, y)   # simple follow function

        :param func: callable, should accept folowing params:
                    glfw_window - glfw window object
                    xpos - window space coordinate x
                    ypos - window space coordinate y
                    mouse - window mouse
                    cursor - this cursor
        :param args: additional arguments to put into func when called
        :param kwargs: additional keyword argument to put into func when called

        :return:
        """
        self.manager.master.mouse.append_cursor_pos_callback(func, *args, **kwargs, cursor=self)

    def set_cursor_enter_callback(self, func):
        raise NotImplementedError

    def set_cursor_exit_callback(self, func):
        raise NotImplementedError


class _Cursor:
    """
    Just a type notifier for IDE
    """

    def __enter__(self) -> Cursor:
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class CursorManager(RenderDeviceManager):
    """
    Manages multitue of `Pane`

    implements global functionalities among Pane
    """

    def __init__(self, device_master):
        super().__init__(device_master)
        # default device
        self.appendnew_cursor((0, 0))

    def __getitem__(self, item) -> _Cursor:
        return super().__getitem__(item)

    @property
    def device_type(self):
        return Cursor

    def appendnew_cursor(self, origin):
        self._appendnew_device(Cursor(origin, self))

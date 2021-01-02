from gkernel.dtype.geometric.primitive import Pnt
from gkernel.dtype.nongeometric.matrix import ScaleMat
from global_tools import Singleton

from ...hooked import *


class _Device:
    def __init__(self, window, manager):
        self.__window = window
        self.__manager = manager
        self.__callback_wrapped = {}

    def _callback_setter(self, callback_func, glfw_type, wrapper):
        wrapped_callback = wrapper(callback_func)
        self.__callback_wrapped.setdefault(glfw_type, set()).add(wrapped_callback)
        return wrapped_callback

    def _run_all_callback(self, *args, device, callback_type):
        """
        Wrapped callback func caller pattern
        :param args: glfw driven callback args
        :param callback_type: callback type indicated with glfw callback setter
        :return:
        """

        for wrapped in self.__callback_wrapped.get(callback_type, []):
            wrapped._run_callback(*args, device)

    @property
    def window(self):
        """
        read only window

        :return: Window instance
        """
        return self.__window

    @property
    def manager(self):
        """
        read only manager

        :return: Manager instance
        """
        return self.__manager


class Mouse(_Device):

    def __init__(self, window, manager):
        super().__init__(window, manager)
        glfw.set_cursor_pos_callback(self.window.glfw_window, self._cursor_pos_callback)

    def _cursor_pos_callback(self, window, xpos, ypos):
        """
        Calls all callbacks joined with 'cursor pos callback'

        :param window:
        :param xpos:
        :param ypos:
        :return:
        """
        xpos, ypos = self.cursor_pos
        self._run_all_callback(window, xpos, ypos, device=self, callback_type=glfw.set_cursor_pos_callback)

    def set_cursor_pos_callback(self, callback_func):
        return self._callback_setter(callback_func, glfw.set_cursor_pos_callback, CursorPosCallbackWrapper)

    def cursor_in_view(self, view, normalize=True):
        """
        Returns cursor position in view coordinate system
        :param view:
        :return:
        """
        transform_matrix = view.glyph.trnsf_matrix.r.I.M
        w, h = self.__manager._window.glyph.size
        unitize_matrix = ScaleMat(1 / w, 1 / h)
        pos = unitize_matrix * transform_matrix * Pnt(*self.cursor_pos)
        if not normalize:
            w, h = view.glyph.size
            view_scale_matrix = ScaleMat(w, h)
            pos = view_scale_matrix*pos
        return pos.x, pos.y

    def intersect_model(self, view, camera, model):
        """

        :param view:
        :param camera:
        :param model:
        :return:
        """
        # 1. convert parameter value into point in space using VM, PM
        #    to create intersection point on near frustum(A)
        # 2. create ray(R) combining using origin(B) and vector from B to A
        # 3. do 'Möller–Trumbore intersection algorithm' with (R) and triangles
        px, py = self.cursor_in_view(view)
        ray = camera.ray_frustum(px, py)
        print(ray.describe())
        # raise NotImplementedError

    @property
    def cursor_pos(self):
        """
        Ask glfw current cursor pos and return

        flips y to match OpenGL coordinate system
        :return:
        """
        _, height = glfw.get_window_size(self.window.glfw_window)
        x, y = glfw.get_cursor_pos(self.window.glfw_window)
        return x, height - y

    def cursor_goto_center(self):
        win = self.window
        glfw.set_cursor_pos(win.glfw_window, win.glyph.width.r / 2, win.glyph.height.r / 2)


class UnknownKeyError(Exception):
    """
    error for unknown key. Shouldn't really happen.
    """
    pass


@Singleton
class GLFWCharDict:
    """
    singleton dictionary for translating glfw callback's key into keyboard char
    """
    # build dict
    __key_char_dict = {}
    __char_key_dict = {}
    __char_shifted_dict = {}
    __shifted_char_dict = {}

    for k, key in glfw.__dict__.items():
        if k.startswith('KEY_'):  # get all constants
            char = k.split('KEY_')[1].lower()
            __key_char_dict[key] = char
    # special cases
    __key_char_dict[glfw.KEY_GRAVE_ACCENT] = '`'
    __key_char_dict[glfw.KEY_MINUS] = '-'
    __key_char_dict[glfw.KEY_EQUAL] = '='
    __key_char_dict[glfw.KEY_LEFT_BRACKET] = '['
    __key_char_dict[glfw.KEY_RIGHT_BRACKET] = ']'
    __key_char_dict[glfw.KEY_BACKSLASH] = "\\"
    __key_char_dict[glfw.KEY_SEMICOLON] = ';'
    __key_char_dict[glfw.KEY_SEMICOLON] = ';'
    __key_char_dict[glfw.KEY_APOSTROPHE] = "'"
    __key_char_dict[glfw.KEY_COMMA] = ","
    __key_char_dict[glfw.KEY_PERIOD] = "."
    __key_char_dict[glfw.KEY_SLASH] = "/"
    # connect char to shifted char
    __char_shifted_dict = {c: s for c, s in zip("`1234567890-=[]\;',./", '~!@#$%^&*()_+{}|:"<>?')}
    # reversed dicts
    __char_key_dict = {v: k for k, v in __key_char_dict.items()}
    __shifted_char_dict = {v: k for k, v in __char_shifted_dict.items()}

    @classmethod
    def key_to_char(cls, key, mods):
        """
        Translate key, mods into char

        :param key: glfw key code
        :param mods: glfw mods code
        :return:
        """
        if key in cls.__key_char_dict:
            char = cls.__key_char_dict[key]
            if mods == glfw.MOD_SHIFT:
                if char in cls.__special_char:
                    return cls.__special_char[char]
                return char.upper()
            return char
        raise UnknownKeyError('input key has to be one of glfw key code')

    @classmethod
    def char_to_key(cls, char):
        """
        translate char into glfw key

        :param char: character of keyboard
        :return:
        """
        # check if shift is pressed?
        if char in cls.__shifted_char_dict:
            return cls.__char_key_dict[cls.__shifted_char_dict[char]]
        elif char in cls.__char_key_dict:
            return cls.__char_key_dict[char]
        else:
            raise UnknownKeyError('char unknown for glfw key code')

    @classmethod
    def get_copied_dict(cls):
        """
        for protect frozen dict, yet to allow custom usage, return copied dict

        :return: copy of code -> char dictionary
        """
        return cls.__key_char_dict.copy()


class Keyboard(_Device):
    __callback_signature = glfw.set_key_callback
    __glfw_key_dict = GLFWCharDict()

    def __init__(self, window, manager):
        super().__init__(window, manager)
        # build key press dict
        # what i want to record is... press status and time
        self.__key_press_dict = self.__glfw_key_dict.get_copied_dict()
        for k, v in self.__key_press_dict.items():
            self.__key_press_dict[k] = [None, 0]  # time, pressed

        glfw.set_key_callback(window.glfw_window, self.__key_callback_master)
        # glfw.set_key_callback(window.glfw_window, self.__key_press_update)

    def append_key_callback(self, callback_func):
        """
        append key callback

        exposed callback setter
        :param callback_func: function to call. Function has to accept all given arguments.
        :return:
        """
        return self._callback_setter(callback_func, glfw.set_key_callback, KeyCallbackWrapper)

    def __key_callback_master(self, *args):
        """
        master key callback calls all other callback of its type

        this is needed to pass Keyboard instance for extended operation
        :param args: arguments passed by glfw event handler
        :return:
        """
        self._run_all_callback(*args, device=self, callback_type=glfw.set_key_callback)

    @classmethod
    def get_char(cls, key, mods):
        """
        Try return char representation of given input

        :param key: input key
        :param mods: mod key, like 'shift' for upper char
        :return: char representation
        """
        return cls.__glfw_key_dict.key_to_char(key, mods)

    def get_key_status(self, *chars):
        return tuple(glfw.get_key(self.window.glfw_window, self.__glfw_key_dict.char_to_key(char)) for char in chars)


class DeviceManager:
    """
    Control group of devices
    """
    def __init__(self, window):
        self._window = window

        self._mouse = Mouse(window, self)
        self._keyboard = Keyboard(window, self)

    @property
    def mouse(self):
        return self._mouse

    @property
    def keyboard(self):
        return self._keyboard



class _CallbackWrapper:
    """
    Needed to add custom-ability into glfw callback
    """

    def __init__(self, func, device):
        self._func = func
        self._device = device

    def _run_callback(self, *args):
        self._func(*args)


class _KeyboardCallbackWrapper(_CallbackWrapper):
    """
    Callback related to keyboard
    """
    def __init__(self, func):
        super().__init__(func, Keyboard)


class _MouseCallbackWrapper(_CallbackWrapper):
    """
    Callback related to mouse
    """
    def __init__(self, func):
        super().__init__(func, Mouse)


class CursorPosCallbackWrapper(_MouseCallbackWrapper):
    """
    Cursor pos callback
    """
    pass


class KeyCallbackWrapper(_KeyboardCallbackWrapper):
    """
    Key press callback
    """
    pass
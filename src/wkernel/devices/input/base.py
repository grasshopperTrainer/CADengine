from gkernel.dtype.geometric.primitive import Pnt
from gkernel.dtype.nongeometric.matrix.primitive import ScaleMat
from global_tools import Singleton, callbackRegistry
import glfw


class _InputDevice:
    def __init__(self, window):
        self.__window = window
        self.__callback_wrapped = {}

    @property
    def window(self):
        """
        read only window

        :return: Window instance
        """
        return self.__window


class Mouse(_InputDevice):

    def __init__(self, window):
        super().__init__(window)
        with window.context.glfw as window:
            glfw.set_cursor_pos_callback(window, self.__master_cursor_pos_callback)

    def __master_cursor_pos_callback(self, window, xpos, ypos):
        """
        Calls all callbacks joined with 'cursor pos callback'

        :param window:
        :param xpos:
        :param ypos:
        :return:
        """
        xpos, ypos = self.cursor_pos
        self.call_cursor_pos_callback(window=window, xpos=xpos, ypos=ypos, mouse=self)

    @callbackRegistry
    def call_cursor_pos_callback(self):
        pass

    @call_cursor_pos_callback.appender
    def append_cursor_pos_callback(self, callbacked, *args, **kwargs):
        """
        append cursor pos callback

        :param callbacked: method should accept following kwargs: window, xpos, ypos, mouse
        :param args: additional arguments to be put when executing (param)callbacked
        :param kwargs: additional kwargs to be put when executing (param)callbacked
        :return:
        """
        pass

    def cursor_in_view(self, view, normalize=True):
        """
        Returns cursor position in view coordinate system
        :param view:
        :return:
        """
        transform_matrix = view.glyph.trnsf_matrix.r.I.M
        w, h = self.window.glyph.size
        unitize_matrix = ScaleMat(1 / w, 1 / h)
        pos = unitize_matrix * transform_matrix * Pnt(*self.cursor_pos)
        if not normalize:
            w, h = view.glyph.size
            view_scale_matrix = ScaleMat(w, h)
            pos = view_scale_matrix * pos
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
        ray = camera.frusrum_ray(px, py)
        print(ray.describe())
        # raise NotImplementedError

    @property
    def cursor_pos(self):
        """
        Ask glfw current cursor pos and return

        flips y to match OpenGL coordinate system
        :return:
        """
        with self.window.context.glfw as window:
            _, height = glfw.get_window_size(window)
            x, y = glfw.get_cursor_pos(window)
        return x, height - y

    def cursor_center(self):
        return tuple(v / 2 for v in self.window.glyph.size)

    def cursor_goto_center(self):
        win = self.window
        with self.window.context.glfw as window:
            glfw.set_cursor_pos(window, win.glyph.w0.r / 2, win.glyph.h0.r / 2)


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


class Keyboard(_InputDevice):
    __callback_signature = glfw.set_key_callback
    __glfw_key_dict = GLFWCharDict()

    def __init__(self, window):
        super().__init__(window)
        # build key press dict
        # what i want to record is... press status and time
        self.__key_press_dict = self.__glfw_key_dict.get_copied_dict()
        for k, v in self.__key_press_dict.items():
            self.__key_press_dict[k] = [None, 0]  # time, pressed
        with window.context.glfw as window:
            glfw.set_key_callback(window, self.__master_key_callback)

    def __master_key_callback(self, window, key, scancode, action, mods):
        """
        master key callback calls all other callback of its type

        method simply does one thing: pass arguments provided by glfw callback handler + self to all key callbacked
        :param window:
        :param key:
        :param scancode:
        :param action:
        :param mods:
        :return:
        """
        self.call_key_callback(window=window, key=key, scancode=scancode, action=action, mods=mods, keyboard=self)

    @callbackRegistry
    def call_key_callback(self, **on_call_kwargs):
        """
        callback caller

        :param on_call_kwargs:
        :return:
        """
        pass

    @call_key_callback.appender
    def append_key_callback(self, callbacked, *args, **kwargs):
        """
        :param callbacked:
        :param args: arguments to put when executing callbacked
        :param kwargs: kwargs to put when executing callbacked
        :return:
        """
        pass

    @call_key_callback.remover
    def remove_key_callback(self, callbacked):
        """
        :param callbacked: function to remove
        :return:
        """
        pass

    @call_key_callback.enabler
    def enable_key_callback(self, v):
        """
        sets activation status of callback calling

        :param v: bool
        :return:
        """
        pass

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
        with self.window.context.glfw as window:
            return tuple(glfw.get_key(window, self.__glfw_key_dict.char_to_key(char)) for char in chars)


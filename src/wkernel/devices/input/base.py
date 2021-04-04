from gkernel.dtype.geometric.primitive import Pnt, Vec
from gkernel.dtype.nongeometric.matrix.primitive import ScaleMat
from global_tools import Singleton, callbackRegistry
import glfw
import numpy as np


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
            glfw.set_cursor_enter_callback(window, self.__master_cursor_enter_callback)
            glfw.set_mouse_button_callback(window, self.__master_mouse_button_callback)
            glfw.set_scroll_callback(window, self.__master_mouse_scroll_callback)
        self.window.append_predraw_callback(self.__set_cursor_pos_perframe)

        self.__pos_perframe = Vec(0, 0, 0)
        self.__pos_prev = Vec(0, 0, 0)
        self.__pos_instant = Vec(0, 0, 0)
        self.__accel = Vec(0, 0, 0)


    def __master_cursor_pos_callback(self, glfw_window, xpos, ypos):
        """
        Calls all callbacks joined with 'cursor pos callback'

        :param glfw_window:
        :param xpos:
        :param ypos:
        :return:
        """
        # flip glfw window space to match OGL space(like texture that has bottom left origin)
        ypos = self.window.glyph.size[1] - ypos

        # update values
        self.__pos_instant = Vec(xpos, ypos, 0)
        self.__accel = self.__pos_instant - self.__pos_prev
        self.__pos_prev = self.__pos_instant

        # call registered callbacks
        self.call_cursor_pos_callback(glfw_window, *self.__pos_instant.xy, mouse=self)

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

    def __master_cursor_enter_callback(self, glfw_window, entered):
        """
        three way callbacking

        :param glfw_window:
        :param entered:
        :return:
        """
        self.call_cursor_enter_callback(glfw_window, entered, mouse=self)

    @callbackRegistry
    def call_cursor_enter_callback(self):
        pass

    @call_cursor_enter_callback.appender
    def append_cursor_enter_callback(self):
        """
        append cursor enter callback
        ! 'enter' also include leaving the window
        :return:
        """

    def __master_mouse_button_callback(self, glfw_window, button, action, mods):
        """

        :param glfw_window:
        :param button:
        :param action:
        :param mods:
        :return:
        """
        self.call_mouse_button_callback(glfw_window, button, action, mods, mouse=self)

    @callbackRegistry
    def call_mouse_button_callback(self):
        pass

    @call_mouse_button_callback.appender
    def append_mouse_button_callback(self):
        pass

    def __master_mouse_scroll_callback(self, glfw_window, xoffset, yoffset):
        """

        :param glfw_window:
        :param xoffset:
        :param yoffset:
        :return:
        """
        self.call_mouse_scroll_callback(glfw_window, xoffset, yoffset, mouse=self)

    @callbackRegistry
    def call_mouse_scroll_callback(self):
        pass

    @call_mouse_scroll_callback.appender
    def append_mouse_scroll_callback(self):
        pass


    @property
    def pos_instant(self):
        """
        Ask glfw event poll thread current cursor pos and return

        flips y to match window coordinate system
        :return:
        """
        return self.__pos_instant

    @property
    def pos_perframe(self):
        """
        cursor pos stored at the beginning of frame drawing

        This is needed as cursor pos is polled by separate thread.
        One has to use this value if it needs a consistent cursor pos during a whole frame drawing

        e.g. FPS camera controlled by cursor movement. Instant cursor_pos called at the beginning and ending
        of frame drawing may return distinct values respectively thus causing perspective anomaly.
        :return:
        """
        return self.__pos_perframe

    @property
    def acceleration(self):
        """
        return cursor x, y acceleration

        :return:
        """
        return self.__accel

    def __set_cursor_pos_perframe(self):
        self.__pos_perframe = self.__pos_instant

    @property
    def cursor_center(self):
        return tuple(v / 2 for v in self.window.glyph.size)

    def cursor_goto_center(self):
        with self.window.context.glfw as window:
            glfw.set_cursor_pos(window, *self.cursor_center)
        self.__pos_perframe = self.cursor_center

    def get_button_status(self, button):
        """
        ask glfw current button status

        :param button: int, {0:left, 1:right, 2:middle}
        :return: current button status
        """
        return glfw.get_mouse_button(self.window.context.glfw_window, button)


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
    __key_char_dict[glfw.KEY_LEFT_SHIFT] = "lshift"
    __key_char_dict[glfw.KEY_RIGHT_SHIFT] = "rshift"
    __key_char_dict[glfw.KEY_LEFT_CONTROL] = "lcontrol"
    __key_char_dict[glfw.KEY_RIGHT_CONTROL] = "rcontrol"
    __key_char_dict[glfw.KEY_LEFT_ALT] = "lalt"
    __key_char_dict[glfw.KEY_RIGHT_ALT] = "rald"
    __key_char_dict[glfw.KEY_LEFT_SUPER] = "lsuper"
    __key_char_dict[glfw.KEY_RIGHT_SUPER] = "rsuper"
    __key_char_dict[glfw.KEY_ESCAPE] = "esc"
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
                # if char in cls.__special_char:
                #     return cls.__special_char[char]
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
    __key_dict = GLFWCharDict()

    def __init__(self, window):
        super().__init__(window)
        # build key press dict
        # what i want to record is... press status and time
        self.__key_press_dict = self.__key_dict.get_copied_dict()
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
        self.call_key_callback(window, key, scancode, action, mods, keyboard=self)

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
        return cls.__key_dict.key_to_char(key, mods)

    def get_key_status(self, char):
        return glfw.get_key(self.window.context.glfw_window, self.__key_dict.char_to_key(char))

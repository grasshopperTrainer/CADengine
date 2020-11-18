from ...hooked import *

class _Device:
    pass


class Mouse(_Device):
    _last_pos = 100, 100

    @classmethod
    def get_last_pos(cls):
        return cls._last_pos


class Keyboard(_Device):
    _callback_signature = glfw.set_key_callback
    # build dict
    _char_dict = {}
    for k, v in glfw.__dict__.items():
        if k.startswith('KEY_'):
            n = k.split('KEY_')[1].lower()
            _char_dict[v] = n
    # special cases
    _char_dict[glfw.KEY_GRAVE_ACCENT] = '`'
    _char_dict[glfw.KEY_MINUS] = '-'
    _char_dict[glfw.KEY_EQUAL] = '='
    _char_dict[glfw.KEY_LEFT_BRACKET] = '['
    _char_dict[glfw.KEY_RIGHT_BRACKET] = ']'
    _char_dict[glfw.KEY_BACKSLASH] = "\\"
    _char_dict[glfw.KEY_SEMICOLON] = ';'
    _char_dict[glfw.KEY_SEMICOLON] = ';'
    _char_dict[glfw.KEY_APOSTROPHE] = "'"
    _char_dict[glfw.KEY_COMMA] = ","
    _char_dict[glfw.KEY_PERIOD] = "."
    _char_dict[glfw.KEY_SLASH] = "/"

    _special_char = {c:s for c, s in zip("`1234567890-=[]\;',./", '~!@#$%^&*()_+{}|:"<>?')}

    @classmethod
    def get_char(cls, key, mods):
        """
        Try return char representation of given input

        :param key: input key
        :param mods: mod key, like 'shift' for upper char
        :return: char representation
        """
        if key in cls._char_dict:
            char = cls._char_dict[key]
            if mods == glfw.MOD_SHIFT:
                if char not in cls._special_char:
                    return char.upper()
                return cls._special_char[char]
            return char
        return None


class DeviceController:
    """
    Control group of devices
    """
    def __init__(self, window):
        self._window = window
        glfw.set_cursor_pos_callback(self._window._glfw_window, self._cursor_pos_callback)
        glfw.set_key_callback(self._window._glfw_window, self._key_callback)
        self._callback_wrapped = {}

    @property
    def window(self):
        return self._window

    def _callback_caller(self, *args, callback_type):
        """
        Wrapped callback func caller pattern
        :param args: glfw driven callback args
        :param callback_type: callback type indicated with glfw callback setter
        :return:
        """

        for wrapped in self._callback_wrapped.get(callback_type):
            wrapped._run_callback(*args)


    def _cursor_pos_callback(self, window, xpos, ypos):
        """
        Calls all callbacks joined with 'cursor pos callback'
        :param window:
        :param xpos:
        :param ypos:
        :return:
        """
        self._callback_caller(window, xpos, ypos, callback_type=glfw.set_cursor_pos_callback)
        # update last pos of cursor
        Mouse._last_pos = xpos, ypos

    def _key_callback(self, window, key, scancode, action, mods):
        """
        Calls all callbacks joined with 'key callback'
        :param window:
        :param key:
        :param scancode:
        :param action:
        :param mods:
        :return:
        """
        self._callback_caller(window, key, scancode, action, mods, callback_type=glfw.set_key_callback)

    def _callback_setter(self, callback_func, glfw_type, wrapper):
        wrapped_callback = wrapper(callback_func)
        self._callback_wrapped.setdefault(glfw_type, set()).add(wrapped_callback)
        return wrapped_callback

    def set_cursor_pos_callback(self, callback_func):
        return self._callback_setter(callback_func, glfw.set_cursor_pos_callback, CursorPosCallback)

    def set_key_callback(self, callback_func):
        return self._callback_setter(callback_func, glfw.set_key_callback, KeyCallback)


class _CallbackWrapper:
    """
    Needed to add custom-ability into glfw callback
    """

    def __init__(self, func, device):
        self._func = func
        self._device = device

    def _run_callback(self, *args):
        self._func(*args, self._device)


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


class CursorPosCallback(_MouseCallbackWrapper):
    """
    Cursor pos callback
    """


class KeyCallback(_KeyboardCallbackWrapper):
    """
    Key press callback
    """
    pass
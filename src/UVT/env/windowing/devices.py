from ...hooked import *

class _Device:
    def __init__(self, glfw_window):
        self._glfw_window = glfw_window
        self._callback_wrapped = {}

    def _callback_setter(self, callback_func, glfw_type, wrapper):
        wrapped_callback = wrapper(callback_func)
        self._callback_wrapped.setdefault(glfw_type, set()).add(wrapped_callback)
        return wrapped_callback

    def _callback_caller(self, *args, callback_type):
        """
        Wrapped callback func caller pattern
        :param args: glfw driven callback args
        :param callback_type: callback type indicated with glfw callback setter
        :return:
        """

        for wrapped in self._callback_wrapped.get(callback_type, []):
            wrapped._run_callback(*args)

    @property
    def glfw_window(self):
        return self._glfw_window


class Mouse(_Device):

    def __init__(self, glfw_window):
        super().__init__(glfw_window)
        glfw.set_cursor_pos_callback(self._glfw_window, self._cursor_pos_callback)

        self._last_pos = 100, 100

    def _cursor_pos_callback(self, window, xpos, ypos):
        """
        Calls all callbacks joined with 'cursor pos callback'
        :param window:
        :param xpos:
        :param ypos:
        :return:
        """
        self._callback_caller(window, xpos, ypos, self, callback_type=glfw.set_cursor_pos_callback)
        # update last pos of cursor
        self._last_pos = xpos, ypos

    def set_cursor_pos_callback(self, callback_func):
        return self._callback_setter(callback_func, glfw.set_cursor_pos_callback, CursorPosCallbackWrapper)

    @property
    def last_pos(self):
        _, height = glfw.get_window_size(self._glfw_window)
        x, y = self._last_pos
        return x, height-y

    @property
    def current_pos(self):
        _, height = glfw.get_window_size(self._glfw_window)
        x, y = glfw.get_cursor_pos(self._glfw_window)
        return x, height-y


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

    def __init__(self, glfw_window):
        super().__init__(glfw_window)
        glfw.set_key_callback(glfw_window, self._key_callback)

    def set_key_callback(self, callback_func):
        return self._callback_setter(callback_func, glfw.set_key_callback, KeyCallbackWrapper)

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
        self._callback_caller(window, key, scancode, action, mods, self, callback_type=glfw.set_key_callback)

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


class DeviceManager:
    """
    Control group of devices
    """
    def __init__(self, window):
        self._window = window

        self._mouse = Mouse(window._glfw_window)
        self._keyboard = Keyboard(window._glfw_window)

    @property
    def window(self):
        return self._window
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
from my_patterns import FamilyMember
from UVT.hooked import glfw


class _Bit(FamilyMember):
    pass


class DrawBit(_Bit):
    """
    has draw call?
    """

    def draw(self):
        """
        Placeholder for chained draw call
        :return:
        """
        if hasattr(self, 'setup') and callable(getattr(self, 'setup')):
            getattr(self, 'setup')()
            for cls in self.__class__.__mro__:
                if 'setup' in cls.__dict__:
                    delattr(cls, 'setup')
                    break

        # call draw method of children
        for c in self.fm_all_children():
            if isinstance(c, DrawBit):
                c.draw()

    def setup(self):
        """
        Instant functions called once
        :return:
        """
        print('setup', self)

class Callbacktype:
    def __init__(self, func):
        self._func = func

    def callback(self, args):
        self._func(*args)


class KeyCallback(Callbacktype):
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

    def get_char(self, key, mods):
        if key in self._char_dict:
            char = self._char_dict[key]
            if mods == glfw.MOD_SHIFT:
                if char not in self._special_char:
                    return char.upper()
                return self._special_char[char]
            return char
        return None

class CursorPosCallback(Callbacktype):
    def __init__(self, func):
        super().__init__(func)
        self.last_pos = (0, 0)

    def callback(self, window, xpos, ypos):
        super().callback((window, xpos, ypos))
        self.last_pos = xpos, ypos


class CallbackMotif(_Bit):
    KEY_CALL = KeyCallback
    CUROSRPOS_CALL = CursorPosCallback


class CallbackBit(CallbackMotif):

    def __init__(self, parent):
        super().__init__()
        self.fm_append_member(parent=parent, child=self)
        self._callback_dict = {}
        self._callback_flag = {}

    def set_callback(self, kind, func):
        if not issubclass(kind, Callbacktype):
            raise TypeError('given is not a callback type')
        handler = kind(func)
        self._callback_dict[kind] = handler
        self._callback_flag.setdefault(kind, True)
        return handler

    def enable_callback(self, kind):
        self._callback_flag[kind] = True

    def disable_callback(self, kind):
        self._callback_flag[kind] = False

    def _callback(self, callback_type, *args):
        if callback_type in self._callback_dict and self._callback_flag[callback_type]:
            self._callback_dict[callback_type].callback(*args)

    @property
    def window(self):
        return self.fm_get_parent(0).window


class CallbackMaster(CallbackMotif):
    def __init__(self, glfw_window):
        super().__init__()
        self._glfw_window = glfw_window
        self.set_callback(glfw.set_key_callback, self.KEY_CALL)
        self.set_callback(glfw.set_cursor_pos_callback, self.CUROSRPOS_CALL)

    def set_callback(self, setter, callback_type):
        def callback(*args):
            for child in self.fm_all_children():
                child._callback(callback_type, *args)
        setter(self._glfw_window, callback)

    @property
    def window(self):
        return self._glfw_window
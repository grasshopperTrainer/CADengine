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

class CallbackMaster(_Bit):
    pass

class CallbackBit(_Bit):

    def __init__(self, parent_bit):
        super().__init__()
        if not isinstance(parent_bit, (self.__class__, CallbackMaster)):
            raise TypeError
        self.fm_append_member(parent_bit, self)

class KeyCallbackBit(CallbackBit):
    """
    Class that listens to window's key callback
    """

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

    def callback(self, *args):
        for child in self.fm_get_ancestor(2,0).fm_all_children():
            if isinstance(child, KeyCallbackBit):
                child.callback(*args)

    def get_char(self, key, mods):
        if key in self._char_dict:
            char = self._char_dict[key]
            if mods == glfw.MOD_SHIFT:
                if char not in self._special_char:
                    return char.upper()
                return self._special_char[char]
            return char
        return None




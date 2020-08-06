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

    _callback_signature = glfw.set_key_callback

    def callback(self, *args):
        for child in self.fm_get_ancestor(2,0).fm_all_children():
            if isinstance(child, KeyCallbackBit):
                child.callback(*args)






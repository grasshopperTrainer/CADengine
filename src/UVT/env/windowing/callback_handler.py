from UVT.hooked import glfwHooked as glfw
from UVT.env.windowing.bits import CallbackBit, KeyCallbackBit
from my_patterns import FamilyMember


class CallbackManager(FamilyMember):

    def __init__(self, window):
        super().__init__()
        self.fm_append_member(window, self)
        self._callbacks = {}

    def set_key_callback(self):
        new_callback = Callback(self, KeyCallbackBit)
        glfw.set_key_callback(self.fm_get_parent(0)._glfw_window, new_callback.callback)
        self._callbacks['key_callback'] = new_callback


class Callback(FamilyMember):
    def __init__(self, handler, callback_bit):
        super().__init__()
        self.fm_append_member(handler, self)
        self._callbackBit = callback_bit
        self._push_flag = True

    def callback(self, *args):
        if self._push_flag:
            for child in self.fm_get_ancestor(2, 0).fm_all_children():
                if isinstance(child, self._callbackBit):
                    child.callback(*args)

    def enable(self):
        self._push_flag = True

    def disable(self):
        self._push_flag = False
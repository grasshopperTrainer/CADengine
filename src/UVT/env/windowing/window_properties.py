from noding import *
from UVT.pipeline.nodes.window import *


class _RenderTargetMember(FamilyMember):
    pass


class RenderTargetPool(_RenderTargetMember):
    def __init__(self, window):
        super().__init__()
        self.fm_append_member(window, self)
        self._current_target_stack = []

    def __getitem__(self, item):
        return self.fm_get_child(item)

    def append_new_target(self, target):
        self.fm_append_member(self, target)

    def current_target(self):
        if self._current_target_stack:
            return self._current_target_stack[-1]
        return None


class RenderTarget(NodeBody):
    pass
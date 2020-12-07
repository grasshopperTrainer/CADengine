from JINTFP import *
from UVT.pipeline.nodes.window import *


# class _RenderTargetMember(FamilyMember):
#     pass


class RenderTarget:
    """
    Instance of render target types
    """
    def __init__(self, pool):
        self._pool = pool

    @property
    def manager(self):
        """
        Render target pool is seen as a 'manager' from its target
        :return:
        """
        return self._pool

class RenderTargetManager:
    def __init__(self, window):
        super().__init__()
        # self.fm_append_member(window, self)
        self._window = window
        self._targets = []
        self._current_target_stack = []

    def __getitem__(self, item) -> RenderTarget:
        raise NotImplementedError

    def _append_new_target(self, target):
        self._targets.append(target)

    def current_target(self):
        if self._current_target_stack:
            return self._current_target_stack[-1]
        return None

    @property
    def window(self):
        return self._window


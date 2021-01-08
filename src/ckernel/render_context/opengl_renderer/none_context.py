from ckernel.glfw_context.none_context import NoneContextManager


class OpenglNoneContext:

    def __init__(self):
        self._cntxt_manager = NoneContextManager()



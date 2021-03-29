from ckernel.glfw_context.none_context import NoneContextManager


class OGLNoneContext:

    def __init__(self):
        self._cntxt_manager = NoneContextManager()

    @property
    def is_none(self):
        return True

    # to ignore all unknown operation
    def __getattr__(self, item):
        return self

    def __call__(self, *args, **kwargs):
        return self
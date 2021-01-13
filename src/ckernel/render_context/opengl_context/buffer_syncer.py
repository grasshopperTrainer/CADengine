from .entity_template import OGLArryBffrTemp


class BufferSyncer:
    """
    handles a pair of cpu, gpu buffer and sync.
    """
    def __init__(self, dtype):
        """
        need struct, need sample array

        :param dtype: structured numpy dtype
        """
        self.__ogl_buffer = OGLArryBffrTemp(dtype)
        raise

    def bind(self):
        pass

    def sync(self):
        pass

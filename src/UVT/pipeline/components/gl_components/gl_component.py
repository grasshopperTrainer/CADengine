from.._component import Component
import weakref as wr


class OpenglComponent(Component):
    """
    OpenGL component type
    """
    def __init__(self, w):
        self._window = wr.ref(w)

    @property
    def is_generated(self) -> bool:
        """
        Check if component is generated inside the context.
        :return:
        """
        if self._id is None:
            return False
        return True

    @property
    def target_win(self):
        if self._window() is None:
            raise Exception('target lost')
        return self._window()

    @property
    def gl(self):
        return self.target_win.gl

    @property
    def is_renderable(self):
        raise NotImplementedError

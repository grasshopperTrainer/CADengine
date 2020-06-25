from.._component import Component, WindowInput

class OpenglComponent(Component):
    """
    OpenGL component type
    """
    window = WindowInput(None)

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
    def gl(self):
        return self.window.gl

    @property
    def is_renderable(self):
        raise NotImplementedError

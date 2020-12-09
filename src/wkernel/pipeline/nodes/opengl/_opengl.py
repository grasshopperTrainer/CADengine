from JINTFP import *
from wkernel.hooked import *
from ...data_types import *


class OpenglNode(NodeBody):
    """
    OpenGL node type
    """

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
    def is_renderable(self):
        raise NotImplementedError

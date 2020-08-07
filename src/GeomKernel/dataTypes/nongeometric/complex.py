from .primitive import *


class TranslationMatrix(Mat4):
    """
    Translation Matrix (move)
    """
    def __init__(self, x=0,y=0,z=0):
        mat = np.eye(4)
        mat[:3, 3] = x, y, z
        super().__init__(mat)


class EyeMat4(Mat4):
    """
    4x4 Identity matrix
    """
    def __init__(self):
        mat = np.eye(4)
        super().__init__(mat)

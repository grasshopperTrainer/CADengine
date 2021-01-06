import numpy as np
from gkernel.constants import ATOL


def iszero(v):
    """
    enough close to zero

    :return:
    """
    return np.isclose(v, 0, atol=ATOL)
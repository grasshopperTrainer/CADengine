import numpy as np

import gkernel.dtype.geometric.primitive as _pr
from .primitive import TrnsfMat

"""
these classes are complex or special
may use geometric primitives, thus had to be separated from primitives
"""


class ViewMatrix(TrnsfMat):

    def __new__(cls, eye, xaxis, yaxis, zaxis):
        """
        calculated matrix is inversed transformation matrix describing world origin to given plane

        :param eye: coordinate of view position in worls
        :param xaxis: coordinate of x axis vector
        :param yaxis: coordinate of y axis vector
        :param zaxis: coordinate of z axis vector
        """
        # to verify axes, anyway need Pln instance
        eye, xaxis, yaxis, zaxis = _pr.Pln(eye, xaxis, yaxis, zaxis).components

        matrix = np.eye(4)
        matrix[0, :3] = xaxis.xyz
        matrix[1, :3] = yaxis.xyz
        matrix[2, :3] = zaxis.xyz
        matrix[:3, 3] = _pr.Vec.dot(-xaxis, eye), _pr.Vec.dot(-yaxis, eye), _pr.Vec.dot(-zaxis, eye)
        return np.array(matrix, dtype=float).view(cls)

    @classmethod
    def from_pln(cls, pln):
        """
        create ViewMatrix from plane
        :param pln: Pln instance
        :return: ViewMatrix
        """
        eye, xaxis, yaxis, zaxis = pln.components
        return cls(eye.xyz, xaxis.xyz, yaxis.xyz, zaxis.xyz)


class ProjectionMatrix(TrnsfMat):

    def __new__(cls, l, r, b, t, n, f, typ):
        """

        :param l: left
        :param r: right
        :param b: bottom
        :param t: top
        :param n: near
        :param f: far
        :param typ: type of projection 'p' for perspective and 'o' for orthographic
        """
        if typ not in ('p', 'o'):
            raise ValueError("type has to be one of: 'p'rojection, 'o'rthographic")

        proj_mat = np.eye(4)
        if typ == 'p':
            if l == -r and b == -t:
                proj_mat[0, 0] = n / r
                proj_mat[1, 1] = n / t
                proj_mat[2, (2, 3)] = -(f + n) / (f - n), -2 * f * n / (f - n)
                proj_mat[3] = 0, 0, -1, 0
            else:
                proj_mat[0, (0, 2)] = 2 * n / (r - l), (r + l) / (r - l)
                proj_mat[1, (1, 2)] = 2 * n / (t - b), (t + b) / (t - b)
                proj_mat[2, (2, 3)] = -(f + n) / (f - n), -2 * f * n / (f - n)
                proj_mat[3] = 0, 0, -1, 0
        else:
            if l == -r and b == -t:
                proj_mat[0, 0] = 1 / r
                proj_mat[1, 1] = 1 / t
                proj_mat[2, (2, 3)] = -2 / (f - n), -(f + n) / (f - n)
                proj_mat[3] = 0, 0, 0, 1
            else:
                proj_mat[0, (0, 3)] = 2 / (r - l), -(r + l) / (r - l)
                proj_mat[1, (1, 3)] = 2 / (t - b), -(t + b) / (t - b)
                proj_mat[2, (2, 3)] = -2 / (f - n), -(f + n) / (f - n)
                proj_mat[3] = 0, 0, 0, 1

        return np.array(proj_mat, dtype=float).view(cls)

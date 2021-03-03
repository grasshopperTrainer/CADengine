"""
! shpae is a renderable thing.
! not all geometry is natively shape.
! think of plane. Its a geometric data but is not !seen!.
! it should be rendered as a box or collection of lines
! `Ray` is also natively not a `Shape`. It may has to be rendered simply as a long `line`.
! distinction: 'native shape, nonnative shape'
"""

import abc


class Shape(metaclass=abc.ABCMeta):
    """
    Interface for a shape object.
    """

    @property
    @abc.abstractmethod
    def geo(self):
        """
        return geometry object of the shape

        Geometry object is a object that stores goemetric data.
        Geometric calculation has to be done using this object and set with resulted to make it updated.
        :return:
        """
        return self.__geo


    def triangulated(self):
        """
        return triangulated form?
        :return:
        """

    def update_array_member(self, mname: str, arr):
        if getattr(self, mname) is None:
            setattr(self, mname, arr)
        else:
            getattr(self, mname)[:] = arr

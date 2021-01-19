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

    @classmethod
    @abc.abstractmethod
    def render(cls):
        """
        render shape face

        :return:
        """
    #
    # @classmethod
    # @abc.abstractmethod
    # def render_line(cls):
    #     """
    #     render shape edge
    #
    #     :return:
    #     """
    #
    # @classmethod
    # @abc.abstractmethod
    # def render_point(cls):
    #     """
    #     render shape vertex
    #
    #     :return:
    #     """
    #
    # @classmethod
    # @abc.abstractmethod
    # def render_default(cls):
    #     """
    #     render default expression
    #
    #     :return:
    #     """

    @abc.abstractmethod
    def intersect(self, ray):
        """
        shape is responsible for intersecting with ray
        :param ray: to intersect with
        :return:
        """
        raise NotImplementedError

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


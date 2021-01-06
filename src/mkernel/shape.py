"""
! shpae is a renderable thing.
! not all geometry is natively shape.
! think of plane. Its a geometric data but is not !seen!.
! it should be rendered as a box or collection of lines
! `Ray` is also natively not a `Shape`. It may has to be rendered simply as a long `line`.
! distinction: 'native shape, nonnative shape'
"""


class Shape:
    """
    Interface for a shape object.
    """

    def intersect(self, ray):
        """
        shape is responsible for intersecting with ray
        :param ray: to intersect with
        :return:
        """
        raise NotImplementedError

    def triangulated(self):
        """
        return triangulated form?
        :return:
        """
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
    def get_cls_renderer(cls):
        """
        return class renderer

        :return:
        """
        return cls.__class__.__renderer

    @abc.abstractmethod
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


class ShapeRenderer:
    """
    Simply is a container for pair of program and buffer.
    """
    def __init__(self, buffer_syncer, gpu_prgrm):
        """
        gpu program doesnt has to be internal; gpu_prgrm can accept anonymous buffer
        But for now leave it as one to one.

        :param buffer_syncer: BufferSyncer instance
        :param gpu_prgrm:
        """
        self.__buffer_syncer = buffer_syncer
        self.__gpu_prgrm = gpu_prgrm

    def render(self):
        """
        running OpenGL operations

        1. bind gpu_buffer
        2. update data from cpu_buffer to gpu_buffer
        3. run gpu_prgrm

        :return:
        """
        # basic binding strategy is to bind then leave it.
        # OpenGL buffer binding is done in sync to push data into gpu
        # so its safe to call push data? but gpu buffer doesn't know it
        # better separate binding to make it explicitly stated
        self.__buffer_syncer.bind()
        self.__buffer_syncer.sync()
        # self.__gpu_prgrm.run_all()

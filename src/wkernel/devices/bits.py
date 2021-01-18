# TODO: deprecate please

import abc


class DrawInterface(metaclass=abc.ABCMeta):
    """
    interface for draw calls
    """

    @abc.abstractmethod
    def draw(self):
        """
        placeholder for glfw and OpenGL operation
        :return:
        """
        pass

    @abc.abstractmethod
    def setup(self):
        """
        instant setting operation before draw

        :return:
        """
        print('ddd')

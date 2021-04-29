import abc
import os

__THIS_PATH = os.path.dirname(__file__)

def get_shader_fullpath(rel_path):
    return os.path.join(__THIS_PATH, rel_path)


class Renderer(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def render(self):
        pass

    # @abc.abstractmethod
    def update_cache(self, shape, arg_name, value):
        pass

    # @abc.abstractmethod
    def add_shape(self, shape):
        pass
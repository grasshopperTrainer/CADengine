import abc
import os

__THIS_PATH = os.path.dirname(__file__)

def get_shader_fullpath(rel_path):
    return os.path.join(__THIS_PATH, rel_path)


class Renderer(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def render(self):
        pass
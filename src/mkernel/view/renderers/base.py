import abc
import os
import weakref as wr


__THIS_PATH = os.path.dirname(__file__)

def get_shader_fullpath(rel_path):
    return os.path.join(__THIS_PATH, rel_path)


class Renderer(metaclass=abc.ABCMeta):
    def __init__(self):
        self.__datasets = wr.WeakKeyDictionary()

    @property
    def datasets(self):
        return self.__datasets

    def malloc_shape(self, shape):
        """
        if present, ignore, else add

        :param shape:
        :return:
        """
        if shape in self.datasets:
            return
        dataset = self.create_dataset(shape.__dataset_size__())
        self.datasets[shape] = dataset
        wr.finalize(shape, self.free_finalizer, dataset)

    def free_shape(self, shape):
        """
        if present, remove

        Think WeakKeyDictionary as a safety measure.
        Modeler will still call this method when shape call itself to `delete`
        :param shape:
        :return:
        """
        if shape not in self.__datasets:
            return
        self.free_finalizer(self.datasets.pop(shape))

    @abc.abstractmethod
    def create_dataset(self, size):
        """
        create new dataset describing shape rendering
        :return:
        """
        pass

    @abc.abstractmethod
    def update_cache(self, shape, arg_name, value):
        pass

    @abc.abstractmethod
    def free_finalizer(self, dataset):
        pass

    @abc.abstractmethod
    def render(self):
        pass


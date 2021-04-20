from .base import NongeoShape



class FlatAxis(NongeoShape):
    def __init__(self, renderer, model):
        self.__vrtx_block = renderer.vbo.cache.request_block(size=4)
        self.__indx_block = renderer.ibo.cache.request_block(size=4)
        self.__indx_block['idx'] = self.__vrtx_block.indices
        self.__vrtx_block['pos'] = (-1, -1), (1, -1), (1, 1), (-1, 1)

        # pixel thickness
        self.__thk = self.thk = 5

    @property
    def thk(self):
        return self.__thk

    @thk.setter
    def thk(self, v):
        self.__thk = v
        self.__vrtx_block['thk'] = v

    def draw_at(self, ray):
        self.__vrtx_block['ori'] = ray.origin.T
        self.__vrtx_block['dir'] = ray.as_vec().T

    def delete(self):
        raise NotImplementedError

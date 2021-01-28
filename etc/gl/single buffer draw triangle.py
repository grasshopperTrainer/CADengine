from UVT import Window, gl
from UVT.doodle import *


class W(Window):
    def __init__(self):
        super().__init__(200, 200, 'window1')

    def setup(self):
        self._inited = False
        self.framerate = 4
        self.count = 0

    def draw(self):
        super().draw()
        if self.count%4 == 2:
            print('a')
            background(0,0,0,0)
            triangle((0, 0, 0), (1, 0, 0), (0, -1, 0))
            triangle((0, 0, 0), (0, 1, 0), (-1, 0, 0))
        elif self.count%4 == 0:
            print('b')
            background(0,0,0,0)
            triangle((0, 0, 0), (1, 0, 0), (0, 1, 0))
            triangle((0, 0, 0), (-1, 0, 0), (0, -1, 0))
        self.count += 1

w = W()
w.run()

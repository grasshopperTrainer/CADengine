from UVT import Window
import UVT.pipeline as comp
import glfw
import numpy as np

# window1 = Window.new_window(200, 200, 'f', monitor=None, shared=None)
# window1.viws.append(0.25,0.25,0.5,0.5)

# class W(Window):
#     def __init__(self):
#         super().__init__(200, 200, 'window1', None, None)
from UVT.patterns import ParentChildren

class C(ParentChildren):
    def draw(self):
        print('this is me')

w = Window(200, 200, 'window1', None, None)
c = C()
w.children_append(c)

w.run()

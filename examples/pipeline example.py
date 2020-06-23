from UVT import Window
from pipeline import Pipeline, comp

import glfw
import numpy as np


pipeline = Pipeline()
a = comp.Integer(10)
b = comp.Integer(5)
addition = comp.Add()
pipeline.relate(a, 'value', 'a', addition)
pipeline.relate(b, 'value', 'b', addition)

pipeline.calc()
print(addition.r)
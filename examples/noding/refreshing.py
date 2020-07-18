from UVT.pipeline.nodes._node import *


class A(NodeBody):
    i = Input()
    o = Output()
    def calculate(self):
        print('calculated')
        self.o = self.i.r*10

class B(NodeBody):
    i = Input()
    o = Output()
    def calculate(self):
        print('calculate B')
        self.o = self.i.r*1.1


a = A()
b = B()
a.i = 20
b.i = a.o
print(b.o)
a.i = 30
print(b.o)
b.refresh()
print(b.o)

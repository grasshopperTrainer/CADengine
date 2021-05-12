"""
! 'simple' characteristic here tells nothing about geometric property.
It merely means are subclasses of `SimpleShape`, meaning rendering requires only
single vertex block and single index block. So geometry covered under this module can have
its 'complex' shape in needing for multi-block support.
"""
from .primitive_wrapper import Vec, Pnt, Lin, Ray, Tgl, Plin
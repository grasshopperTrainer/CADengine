import numpy as np
from collections import namedtuple


print(np.float64.dtype, type(np.float64))
print(np.dtype(np.float32))

# building array with single field with multiple values
values = [[1,2,3], [4,5,6], [7,8,9]]
values = [tuple([tuple(chunk)]) for chunk in values]
print(values)
dtype = np.dtype([('coord', 'f', 3)])
arr = np.array(values, dtype=dtype)
print(arr, '\n')

# adding new row to it
row = np.array(([10,11,12],), dtype=dtype)
arr = np.append(arr, row)
print(arr,'\n')

# checking itemsize
print(arr.itemsize) # item size of a row
print('total byte', arr.itemsize*arr.size)
print(arr['coord'].itemsize)    # item size of a single element

d = np.dtype([('a', 'f8', 3), ('b', 'f', 2), ('c', 'f', 3)])

nt = namedtuple('vao_properties', ('name', 'size', 'type', 'stride', 'offset'))
nts = []
stride = 10
for k, v in d.fields.items():
    dtype, offset = v
    subdtype, size = dtype.subdtype
    size = size[0]
    print(subdtype)
    print(nt(k, size, subdtype, stride, offset))

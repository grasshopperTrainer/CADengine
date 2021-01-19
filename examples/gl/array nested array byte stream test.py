import glfw
import OpenGL.GL as gl
import numpy as np
from gkernel.dtype.geometric.primitive import Pnt, Tgl
from gkernel.dtype.nongeometric.matrix.primitive import MoveMat

# test for single vertex, color interleaved
# prepare context
glfw.init()
w = glfw.create_window(100, 100, '4', None, None)
glfw.make_context_current(w)
a = gl.glGenBuffers(1)
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, a)

# build array
dtype = np.dtype([('pnt', 'f4', 4), ('clr', 'f4', 3)])
raw_arr = [((0, 0, 0, 0), (1, 1, 1)), ((0, 0, 0, 0), (1, 1, 1))]
arr = np.array(raw_arr, dtype=dtype)

# modify viewed
p0 = arr['pnt'][0].reshape(4, 1).view(Pnt)
p0[0] = 1

# push data
gl.glBufferData(target=gl.GL_ARRAY_BUFFER, size=32, data=arr, usage=gl.GL_STATIC_DRAW)
# check buffer
k = gl.glGetBufferSubData(gl.GL_ARRAY_BUFFER, 0, 32)
print(k, len(k))

glfw.terminate()
print()

# test for m
# prepare context
glfw.init()
w = glfw.create_window(100, 100, '4', None, None)
glfw.make_context_current(w)
a = gl.glGenBuffers(1)
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, a)

# build array
dtype = np.dtype([('pnt', 'f4', 4), ('clr', 'f4', 3)])
raw_arr = [((0, 0, 0, 1), (1, 1, 1)), ((0, 0, 0, 1), (1, 1, 1)), ((0, 0, 0, 1), (1, 1, 1))]
arr = np.array(raw_arr, dtype=dtype)
print(arr)
# modify viewed
tgl = arr['pnt'][0:3].T.view(Tgl)
tgl[:] = MoveMat(10, 10, 10) * tgl
print(arr)

# push data
gl.glBufferData(target=gl.GL_ARRAY_BUFFER, size=84, data=arr, usage=gl.GL_STATIC_DRAW)
# check buffer
k = gl.glGetBufferSubData(gl.GL_ARRAY_BUFFER, 0, 84)
print(k, len(k))

glfw.terminate()
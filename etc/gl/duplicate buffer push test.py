import glfw
import OpenGL.GL as gl
import time

"""
conclusion:
    redundant binding seems to be not ignored by OpenGL context,
    but is it hardware wise is not tested.
"""
# prepare context
glfw.init()
w = glfw.create_window(100, 100, '4', None, None)
glfw.make_context_current(w)
# create buffers
n = 10000
buffer = gl.glGenBuffers(1)
buffers = [gl.glGenBuffers(1) for _ in range(n)]
# iteration time
iter_time = None
s = time.time()
for i in range(n):
    pass
e = time.time()
iter_time = e - s
print(iter_time)
# redundant binding lead time
s = time.time()
for i in range(n):
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)
e = time.time()
print(e-s-iter_time)
# meaningful binding lead time
s = time.time()
for b in buffers:
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, b)
e = time.time()
print(e-s-iter_time)

glfw.terminate()

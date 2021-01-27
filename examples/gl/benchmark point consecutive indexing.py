import glfw
import OpenGL.GL as gl
import random
import numpy as np
import ctypes
import time

"""
result: no indexing is faster
but there is no much difference between random and consecutive indexing
"""

glfw.init()
window = glfw.create_window(1000, 1000, 'mywindow', None, None)
glfw.make_context_current(window)

# create points
points = []
num_points = 10_000_000
for _ in range(num_points):
    point = [random.uniform(-1, 1), random.uniform(-1, 1), 0]
    points.append(point)
points = np.array(points, dtype='f4')

# create index
consecutive_idx = np.array([i for i in range(num_points)], dtype='uint')
random_idx = list(range(num_points))
random.shuffle(random_idx)
random_idx = np.array(random_idx, dtype='uint')

# create program
vrtx = """
#version 450 core

layout (location = 0) in vec4 vtx;

void main() {
    gl_Position = vtx;
}
"""

frgm = """
#version 450 core


out vec4 FragColor;

void main() {
    FragColor = vec4(1, 1, 0, 1);
}
"""
vs = gl.glCreateShader(gl.GL_VERTEX_SHADER)
gl.glShaderSource(vs, vrtx)
gl.glCompileShader(vs)
fs = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
gl.glShaderSource(fs, frgm)
gl.glCompileShader(vs)

prgrm = gl.glCreateProgram()
gl.glAttachShader(prgrm, vs)
gl.glAttachShader(prgrm, fs)
gl.glLinkProgram(prgrm)
gl.glUseProgram(prgrm)
# create buffers
vbo = gl.glGenBuffers(1)
consecutive_ibo = gl.glGenBuffers(1)
random_ibo = gl.glGenBuffers(1)

# push consecutive data
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
gl.glBufferData(gl.GL_ARRAY_BUFFER,
                points.itemsize * points.size,
                points,
                gl.GL_DYNAMIC_DRAW)

gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, consecutive_ibo)
gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,
                consecutive_idx.itemsize * consecutive_idx.size,
                consecutive_idx,
                gl.GL_DYNAMIC_DRAW)
gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, random_ibo)
gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,
                random_idx.itemsize * random_idx.size,
                random_idx,
                gl.GL_DYNAMIC_DRAW)

gl.glEnable(gl.GL_PROGRAM_POINT_SIZE)
gl.glPointSize(1)

gl.glEnableVertexAttribArray(0)
gl.glVertexAttribPointer(index=0,
                         size=3,
                         type=gl.GL_FLOAT,
                         normalized=gl.GL_FALSE,
                         stride=12,
                         pointer=ctypes.c_void_p(0))
# render
num_test = 1000
# clean background
gl.glClearColor(0, 0, 0, 0)
gl.glClear(gl.GL_COLOR_BUFFER_BIT)


gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, random_ibo)
summed = 0
for i in range(num_test):
    s = time.time()
    gl.glDrawElements(gl.GL_POINTS,
                      num_points,
                      gl.GL_UNSIGNED_INT,
                      ctypes.c_void_p(0))
    e = time.time()
    summed += e - s
print('random indexing:', summed / num_test)

gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, consecutive_ibo)
summed = 0
for i in range(num_test):
    s = time.time()
    gl.glDrawElements(gl.GL_POINTS,
                      num_points,
                      gl.GL_UNSIGNED_INT,
                      ctypes.c_void_p(0))
    e = time.time()
    summed += e-s
print('consecutive indexing:', summed/num_test)

summed = 0
for i in range(num_test):
    s = time.time()
    gl.glDrawArrays(gl.GL_POINTS, 0, num_points)
    e = time.time()
    summed += e - s
print('no indexing:', summed / num_test)


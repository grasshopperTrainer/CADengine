import glfw
import OpenGL.GL as gl
import random
import numpy as np
import ctypes
import time

"""

"""

glfw.init()
window = glfw.create_window(1000, 1000, 'mywindow', None, None)
glfw.make_context_current(window)

# create points
points = []
num_points = 1_000_000
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
# set attribute pointer
gl.glEnableVertexAttribArray(0)
gl.glVertexAttribPointer(index=0,
                         size=3,
                         type=gl.GL_FLOAT,
                         normalized=gl.GL_FALSE,
                         stride=12,
                         pointer=ctypes.c_void_p(0))

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
# prepare query
query = gl.glGenQueries(1)[0]

# prepare render
gl.glEnable(gl.GL_PROGRAM_POINT_SIZE)
gl.glPointSize(1)
# clean background
gl.glClearColor(0, 0, 0, 0)
gl.glClear(gl.GL_COLOR_BUFFER_BIT)

# test
num_test = 100
gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, random_ibo)
elapse_times = []
for _ in range(num_test):
    gl.glBeginQuery(gl.GL_TIME_ELAPSED, query)
    gl.glDrawElements(gl.GL_TRIANGLES,
                      num_points,
                      gl.GL_UNSIGNED_INT,
                      ctypes.c_void_p(0))
    gl.glEndQuery(gl.GL_TIME_ELAPSED)
    elapse_times.append(gl.glGetQueryObjectiv(query, gl.GL_QUERY_RESULT))
print('random indexing:', sum(t/num_test for t in elapse_times) / 1_000_000_000)

gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, consecutive_ibo)
elapse_times = []
for _ in range(num_test):
    gl.glBeginQuery(gl.GL_TIME_ELAPSED, query)
    gl.glDrawElements(gl.GL_TRIANGLES,
                      num_points,
                      gl.GL_UNSIGNED_INT,
                      ctypes.c_void_p(0))
    gl.glEndQuery(gl.GL_TIME_ELAPSED)
    elapse_times.append(gl.glGetQueryObjectiv(query, gl.GL_QUERY_RESULT))
print('consecutive indexing:', sum(t/num_test for t in elapse_times) / 1_000_000_000)

gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)
elapse_times = []
for _ in range(num_test):
    gl.glBeginQuery(gl.GL_TIME_ELAPSED, query)
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, num_points)
    gl.glEndQuery(gl.GL_TIME_ELAPSED)
    elapse_times.append(gl.glGetQueryObjectiv(query, gl.GL_QUERY_RESULT))
print('no indexing:', sum(t/num_test for t in elapse_times) / 1_000_000_000)

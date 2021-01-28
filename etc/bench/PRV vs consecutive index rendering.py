import glfw
import OpenGL.GL as gl
import random
import numpy as np
import ctypes
import time

"""
benchmark if Primitive Reset Value is actually discarded in render pipeline thus saves time.

PRV actually makes sense. Only time spent is itering all the indices. so 

result: (elapse time in seconds)
TEST render triangles PRV indexing RESULT: 0.0007646921600000001
TEST render points PRV indexing RESULT: 0.0007367337600000002
TEST render triangles consecutive indexing RESULT: 0.13444233311999998
TEST render points no indexing RESULT: 8.275263999999999e-05
"""

glfw.init()
window = glfw.create_window(1000, 1000, 'mywindow', None, None)
glfw.make_context_current(window)

# prepare array
num_points = 1_000_000
dtype = np.dtype([('vtx', 'f4', 4), ('clr', 'f4', 4)])
points = np.ndarray(num_points, dtype)
# create points
for i in range(num_points):
    point = [random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)]
    color = [random.random(), random.random(), random.random(), random.random()]
    points[i] = point, color

# create index
consecutive_idx = np.array([i for i in range(num_points)], dtype='uint')
prv_idx = np.array([0xff_ff_ff_ff for _ in range(num_points)], dtype='uint')

# create program
vrtx = """
#version 450 core

layout (location = 0) in vec4 vtx;
layout (location = 1) in vec4 clr;

out vec4 fclr;

void main() {
    gl_Position = vtx;
    fclr = clr;
}
"""

frgm = """
#version 450 core

in vec4 fclr;
out vec4 FragColor;

void main() {
    FragColor = fclr;
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
prv_ibo = gl.glGenBuffers(1)

# push consecutive data
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
gl.glBufferData(gl.GL_ARRAY_BUFFER,
                points.itemsize * points.size,
                points,
                gl.GL_DYNAMIC_DRAW)
# set attribute pointer
gl.glEnableVertexAttribArray(0)
gl.glVertexAttribPointer(index=0,
                         size=4,
                         type=gl.GL_FLOAT,
                         normalized=gl.GL_FALSE,
                         stride=32,
                         pointer=ctypes.c_void_p(0))
gl.glEnableVertexAttribArray(1)
gl.glVertexAttribPointer(index=1,
                         size=4,
                         type=gl.GL_FLOAT,
                         normalized=gl.GL_FALSE,
                         stride=32,
                         pointer=ctypes.c_void_p(16))

gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, consecutive_ibo)
gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,
                consecutive_idx.itemsize * consecutive_idx.size,
                consecutive_idx,
                gl.GL_DYNAMIC_DRAW)
gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, prv_ibo)
gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,
                prv_idx.itemsize * prv_idx.size,
                prv_idx,
                gl.GL_DYNAMIC_DRAW)
# prepare query
qid = gl.glGenQueries(1)[0]

# prepare render
gl.glEnable(gl.GL_PRIMITIVE_RESTART_FIXED_INDEX)
gl.glEnable(gl.GL_PROGRAM_POINT_SIZE)
gl.glPointSize(1)
# clean background
gl.glClearColor(0, 0, 0, 0)
gl.glClear(gl.GL_COLOR_BUFFER_BIT)


# test
def test(setting, query, num_test, test_name):
    setting()
    elapse_times = []
    for i in range(num_test):
        gl.glBeginQuery(gl.GL_TIME_ELAPSED, qid)
        query()
        gl.glEndQuery(gl.GL_TIME_ELAPSED)
        elapse_times.append(gl.glGetQueryObjectiv(qid, gl.GL_QUERY_RESULT))
    glfw.swap_buffers(window)
    ave = sum(t / num_test for t in elapse_times) / 1_000_000_000
    print(f"TEST {test_name} RESULT: {ave}")


num_test = 100
is_test = True
while not glfw.window_should_close(window):
    if is_test:
        test(setting=lambda: gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, prv_ibo),
             query=lambda: gl.glDrawElements(gl.GL_TRIANGLES,
                                             num_points,
                                             gl.GL_UNSIGNED_INT,
                                             ctypes.c_void_p(0)),
             num_test=num_test,
             test_name='render triangles PRV indexing')
        test(setting=lambda: gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, prv_ibo),
             query=lambda: gl.glDrawElements(gl.GL_POINTS,
                                             num_points,
                                             gl.GL_UNSIGNED_INT,
                                             ctypes.c_void_p(0)),
             num_test=num_test,
             test_name='render points PRV indexing')
        test(setting=lambda: gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, consecutive_ibo),
             query=lambda: gl.glDrawElements(gl.GL_TRIANGLES,
                              num_points,
                              gl.GL_UNSIGNED_INT,
                              ctypes.c_void_p(0)),
             num_test=num_test,
             test_name='render triangles consecutive indexing')
        test(setting=lambda: gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0),
             query=lambda: gl.glDrawArrays(gl.GL_POINTS, 0, num_points),
             num_test=num_test,
             test_name='render points no indexing')
        is_test = False
        print('TEST DONE')
    glfw.poll_events()
    time.sleep(1/60)    # check result and wait for close

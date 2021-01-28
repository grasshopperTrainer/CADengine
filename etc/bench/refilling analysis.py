import glfw
import OpenGL.GL as gl
import random
import numpy as np
import ctypes
import time
from ckernel.render_context.opengl_context.bffr_cache import BffrCache

"""
benchmark:
elapse time profile for rendering with tight packing

result: (job, time in second, share in elapse time)
refill 10.757270574569702 77.6881393283%
push_packed 3.25824e-05 0.0002353075%
render_packed 9.12e-06 6.58639e-05%
restore 3.0894084692001345 22.3114584628%
repush 2.144e-06 1.54838e-05%
rerender 1.18464e-05 8.55537e-05%

conclusion:
Packing is good when done behind, silently, but unusable if done vertex by vertex in frame render time.
Case it could be compatible in frame render time is when a (really)big block is released. But even then
simply rendering all will be faster. But packing is still a method of reducing render time if it could be
done asynchronously.
"""

glfw.init()
window = glfw.create_window(1000, 1000, 'mywindow', None, None)
glfw.make_context_current(window)

# prepare data
num_points = 100000
dtype = np.dtype([('vtx', 'f4', 4), ('clr', 'f4', 4)])
points = np.ndarray(num_points, dtype)

# create index
test1_idx = BffrCache(np.dtype([('idx', 'uint')]), (0,), size=num_points)
test1_blocks = []

# create points
for i in range(num_points):
    point = [random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)]
    color = [random.random(), random.random(), random.random(), random.random()]
    points[i] = point, color

    b1 = test1_idx.request_block(size=1)
    b1['idx'] = i
    test1_blocks.append(b1)


# prepare indices to replace
pick_rate = 0.5
i = list(range(num_points))
cherry_picked = []
for i in range(int(num_points * pick_rate)):
    cherry_picked.append(i)

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
test1_ibo = gl.glGenBuffers(1)
test2_ibo = gl.glGenBuffers(1)
test3_ibo = gl.glGenBuffers(1)

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

gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, test1_ibo)
gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,
                test1_idx.active_bytesize,
                test1_idx.array,
                gl.GL_DYNAMIC_DRAW)

# prepare render
gl.glEnable(gl.GL_PRIMITIVE_RESTART_FIXED_INDEX)
gl.glEnable(gl.GL_PROGRAM_POINT_SIZE)
gl.glPointSize(1)
# clean background
gl.glClearColor(0, 0, 0, 0)
gl.glClear(gl.GL_COLOR_BUFFER_BIT)

qid = gl.glGenQueries(1)[0]

# test
num_test = 10
is_test = True
times = {}
for _ in range(num_test):
    removed = []
    # pick
    s = time.time()
    for i in cherry_picked:
        block = test1_blocks[i]
        removed.append(block['idx'][:])
        block.release_refill(0xff_ff_ff_ff)
    e = time.time()
    times.setdefault('refill', []).append(e-s)

    # push data
    gl.glBeginQuery(gl.GL_TIME_ELAPSED, qid)
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, test3_ibo)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,
                    test1_idx.active_bytesize,
                    test1_idx.array,
                    gl.GL_DYNAMIC_DRAW)
    gl.glEndQuery(gl.GL_TIME_ELAPSED)
    times.setdefault('push_packed', []).append(gl.glGetQueryObjectiv(qid, gl.GL_QUERY_RESULT)/1_000_000_000)

    # render
    gl.glBeginQuery(gl.GL_TIME_ELAPSED, qid)
    gl.glDrawElements(gl.GL_POINTS,
                      test1_idx.highest_indx + 1,
                      gl.GL_UNSIGNED_INT,
                      ctypes.c_void_p(0))
    gl.glEndQuery(gl.GL_TIME_ELAPSED)
    times.setdefault('render_packed', []).append(gl.glGetQueryObjectiv(qid, gl.GL_QUERY_RESULT)/1_000_000_000)

    # reset
    s = time.time()
    for i in cherry_picked:
        new_block = test1_idx.request_block(size=1)
        new_block['idx'] = removed[i]
        test1_blocks[i] = new_block
    e = time.time()
    times.setdefault('restore', []).append(e-s)

    # repush data
    gl.glBeginQuery(gl.GL_TIME_ELAPSED, qid)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,
                    test1_idx.active_bytesize,
                    test1_idx.array,
                    gl.GL_DYNAMIC_DRAW)
    gl.glEndQuery(gl.GL_TIME_ELAPSED)
    times.setdefault('repush', []).append(gl.glGetQueryObjectiv(qid, gl.GL_QUERY_RESULT)/1_000_000_000)

    # re render
    gl.glBeginQuery(gl.GL_TIME_ELAPSED, qid)
    gl.glDrawElements(gl.GL_POINTS,
                      test1_idx.highest_indx + 1,
                      gl.GL_UNSIGNED_INT,
                      ctypes.c_void_p(0))
    gl.glEndQuery(gl.GL_TIME_ELAPSED)
    times.setdefault('rerender', []).append(gl.glGetQueryObjectiv(qid, gl.GL_QUERY_RESULT)/1_000_000_000)

for k, v in times.items():
    v.sort()
    times[k] = sum(v[int(num_test*0.05):int(num_test*0.95)])/num_test
summed_t = sum(times.values())
for k, v in times.items():
    print(k, v, f"{round((v/summed_t)*100, 10)}%")
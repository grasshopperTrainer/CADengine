import glfw
import OpenGL.GL as gl
import random
import numpy as np
import ctypes
import time
from ckernel.render_context.opengl_context.bffr_cache import BffrCache

"""
benchmark:
assigning PRV values out of A% indices -> 
render with full length index buffer -> 
reassigning indices and render again
vs
remove indices by A% and tightly pack -> 
render with shortened index buffer -> 
reassign indices and render again

In other words, want to know whether time used to pack tightly is worthy


result:
! RENDERING ELAPSE TIME is not purely GPU rendering time. it includes overhead organizing cache, block objects

release-refilling 50%:
TEST set_PRV_render_full_length RENDERING ELAPSE TIME: 0.002141264
TEST set_PRV_render_full_length FULL ELAPSE TIME: 0.4623196601867676

TEST release_no_pack RENDERING ELAPSE TIME: 0.0025272032
TEST release_no_pack FULL ELAPSE TIME: 7.461874794960022

TEST remove_render_tightly_packed RENDERING ELAPSE TIME: 1.0737603419000001
TEST remove_render_tightly_packed FULL ELAPSE TIME: 16.600671648979187


conclusion:
Index tight packing reduces number of indices to render but packing itself takes too much time.
Therefore release_fill operation is not fast enough to be executed commonly in frame-time.
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
test2_idx = BffrCache(np.dtype([('idx', 'uint')]), (0,), size=num_points)
test3_idx = BffrCache(np.dtype([('idx', 'uint')]), (0,), size=num_points)
test1_blocks = []
test2_blocks = []
test3_blocks = []

# create points
for i in range(num_points):
    point = [random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)]
    color = [random.random(), random.random(), random.random(), random.random()]
    points[i] = point, color

    b1 = test1_idx.request_block(size=1)
    b1['idx'] = i
    test1_blocks.append(b1)

    b2 = test2_idx.request_block(size=1)
    b2['idx'] = i
    test2_blocks.append(b2)

    b3 = test3_idx.request_block(size=1)
    b3['idx'] = i
    test3_blocks.append(b3)

# prepare indices to replace
pick_rate = 0.9
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
gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, test2_ibo)
gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,
                test2_idx.active_bytesize,
                test2_idx.array,
                gl.GL_DYNAMIC_DRAW)
gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, test3_ibo)
gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,
                test3_idx.active_bytesize,
                test3_idx.array,
                gl.GL_DYNAMIC_DRAW)
gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)

# prepare render
gl.glEnable(gl.GL_PRIMITIVE_RESTART_FIXED_INDEX)
gl.glEnable(gl.GL_PROGRAM_POINT_SIZE)
gl.glPointSize(1)
# clean background
gl.glClearColor(0, 0, 0, 0)
gl.glClear(gl.GL_COLOR_BUFFER_BIT)


# test
def benchmark(num_test, query, preset=lambda: (), test_name=None):
    qid = gl.glGenQueries(1)[0]

    preset()
    render_times = []
    operation_times = []
    for i in range(num_test):
        s = time.time()
        gl.glBeginQuery(gl.GL_TIME_ELAPSED, qid)
        query()
        gl.glEndQuery(gl.GL_TIME_ELAPSED)
        e = time.time()
        operation_times.append(e-s)
        while not gl.glGetQueryObjectiv(qid, gl.GL_QUERY_RESULT_AVAILABLE):
            pass
        render_times.append(gl.glGetQueryObjectiv(qid, gl.GL_QUERY_RESULT))
    glfw.swap_buffers(window)
    gl.glDeleteQueries(1, [qid])

    truncated_ratio = 0.95
    render_times.sort()
    render_times = render_times[int(len(render_times)*(1-truncated_ratio)):int(len(render_times)*truncated_ratio)]
    render_ave = sum(t / num_test for t in render_times) / 1_000_000_000
    operation_times.sort()
    operation_times = operation_times[int(len(operation_times)*(1-truncated_ratio)):int(len(operation_times)*truncated_ratio)]
    op_ave = sum(t / num_test for t in operation_times)
    if test_name is None:
        test_name = query.__name__
    print(f"TEST {test_name} RENDERING ELAPSE TIME: {render_ave}")
    print(f"TEST {test_name} FULL ELAPSE TIME: {op_ave}")
    print()


def set_PRV_render_full_length():
    """
    assign PRV and maintain all blocks
    :return:
    """
    removed = []
    # pick
    for i in cherry_picked:
        block = test1_blocks[i]
        removed.append(block['idx'][:])
        block['idx'] = 0xff_ff_ff_ff
    # push data
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, test1_ibo)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,
                    test1_idx.active_bytesize,
                    test1_idx.array,
                    gl.GL_DYNAMIC_DRAW)
    # print(test1_idx.highest_indx, test1_idx.active_bytesize)
    # render
    gl.glDrawElements(gl.GL_POINTS,
                      test1_idx.highest_indx + 1,
                      gl.GL_UNSIGNED_INT,
                      ctypes.c_void_p(0))
    # reset
    for i in cherry_picked:
        test1_idx[i]['idx'] = removed[i]
    # push data

    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,
                    test1_idx.active_bytesize,
                    test1_idx.array,
                    gl.GL_DYNAMIC_DRAW)
    # re render
    gl.glDrawElements(gl.GL_POINTS,
                      test1_idx.highest_indx + 1,
                      gl.GL_UNSIGNED_INT,
                      ctypes.c_void_p(0))


def remove_render_tightly_packed():
    """
    for every block released, pack tight
    :return:
    """
    removed = []
    # pick
    for i in cherry_picked:
        block = test3_blocks[i]
        removed.append(block['idx'][:])
        block.release_refill(0xff_ff_ff_ff)
    # push data
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, test3_ibo)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,
                    test3_idx.active_bytesize,
                    test3_idx.array,
                    gl.GL_DYNAMIC_DRAW)
    # print(test3_idx.highest_indx, test3_idx.active_bytesize)
    # render
    gl.glDrawElements(gl.GL_POINTS,
                      test3_idx.highest_indx + 1,
                      gl.GL_UNSIGNED_INT,
                      ctypes.c_void_p(0))

    # reset
    for i in cherry_picked:
        new_block = test3_idx.request_block(size=1)
        new_block['idx'] = removed[i]
        test3_blocks[i] = new_block

    # repush data
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,
                    test3_idx.active_bytesize,
                    test3_idx.array,
                    gl.GL_DYNAMIC_DRAW)
    # re render
    gl.glDrawElements(gl.GL_POINTS,
                      test3_idx.highest_indx + 1,
                      gl.GL_UNSIGNED_INT,
                      ctypes.c_void_p(0))


def release_no_pack():
    """
    this releases block but do not pack tight
    :return:
    """
    removed = []
    # pick
    for i in cherry_picked:
        block = test2_blocks[i]
        removed.append(block['idx'][:])
        block.release(0xff_ff_ff_ff)

    # push data
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, test2_ibo)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,
                    test2_idx.active_bytesize,
                    test2_idx.array,
                    gl.GL_DYNAMIC_DRAW)
    # print(test2_idx.highest_indx, test2_idx.active_bytesize)
    # render
    gl.glDrawElements(gl.GL_POINTS,
                      test2_idx.highest_indx + 1,
                      gl.GL_UNSIGNED_INT,
                      ctypes.c_void_p(0))
    # reset
    for i in cherry_picked:
        new_block = test2_idx.request_block(size=1)
        new_block['idx'] = removed[i]
        test2_blocks[i] = new_block
    # repush data
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,
                    test2_idx.active_bytesize,
                    test2_idx.array,
                    gl.GL_DYNAMIC_DRAW)
    # re render
    gl.glDrawElements(gl.GL_POINTS,
                      test2_idx.highest_indx + 1,
                      gl.GL_UNSIGNED_INT,
                      ctypes.c_void_p(0))


num_test = 10
is_test = True
while not glfw.window_should_close(window):
    if is_test:
        benchmark(num_test=num_test,
                  query=set_PRV_render_full_length,
                  preset=lambda: gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0))
        benchmark(num_test=num_test,
                  query=remove_render_tightly_packed,
                  preset=lambda: gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0))
        benchmark(num_test=num_test,
                  query=release_no_pack,
                  preset=lambda: gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0))
        is_test = False
        print('TEST DONE')
    glfw.poll_events()
    time.sleep(1 / 60)  # check result and wait for close
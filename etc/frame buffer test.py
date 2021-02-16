import ckernel.render_context.opengl_context.meta_entities as meta
import time
import glfw
import ckernel.render_context.opengl_context.opengl_hooker as gl
glfw.init()
glfw.make_context_current(glfw.create_window(100, 100, 'a', None, None))
s = time.time()
k = gl.glGenBuffers(1000)
e = time.time()
print(e-s)
print(type(k))
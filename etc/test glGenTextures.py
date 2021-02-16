import numpy as np
import OpenGL.GL as gl
import glfw

# initiating context
glfw.init()
w = glfw.create_window(100, 100, 'dd', None, None)
glfw.make_context_current(w)

# prepare two sample image
w0, h0 = 8, 3
value = 1
image0 = np.array([value for i in range(w0 * h0 * 3)], dtype='ubyte')

w1, h1 = 4, 5
value = 2
image1 = np.array([value for i in range(w1 * h1 * 3)], dtype='ubyte')

# gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
# prepare texture
t = gl.glGenTextures(1)
gl.glBindTexture(gl.GL_TEXTURE_2D, t)
iformat = gl.GL_RGB

# prepare debugger
def read_display(w, h):
    # read texture
    p = gl.glGetTexImage(gl.GL_TEXTURE_2D, 0, iformat, gl.GL_UNSIGNED_BYTE)

    # display pixel values
    pixels = iter(p)
    for x in range(w):
        vs = []
        for y in range(h):
            vs.append((next(pixels), next(pixels), next(pixels)))
        print(vs)

# first text
# upload texture
gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, iformat, w0, h0, 0, iformat, gl.GL_UNSIGNED_BYTE, image0)
read_display(w0, h0)
print()

# upload once more
gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, iformat, w1, h1, 0, iformat, gl.GL_UNSIGNED_BYTE, image1)
read_display(w1, h1)

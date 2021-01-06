import wkernel.hooked.openglHooked as gl
from wkernel.env.windows import Windows


def background(r=None,g=None,b=None,a=None):
    if not all([i is None for i in (r,g,b,a)]):
        gl.glClearColor(r, g, b, a)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

def noloop():
    Windows.get_current()._is_loop = False

# def swap():
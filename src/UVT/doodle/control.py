from UVT.patterns import SingletonClass
from UVT.env.draw_bit import DrawBit
import UVT.hooked.openglHooked as gl
import UVT.pipeline.nodes as node
from UVT.env.windows import Windows

def background(r=None,g=None,b=None,a=None):
    if not all([i is None for i in (r,g,b,a)]):
        gl.glClearColor(r, g, b, a)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

def noloop():
    Windows.get_current()._is_loop = False

# def swap():
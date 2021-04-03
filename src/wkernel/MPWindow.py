import glfw
import OpenGL.GL as gl
from multiprocessing.managers import BaseManager
import multiprocessing as mp
import time


class MyManager(BaseManager):
    pass


class Window:
    def __init__(self):
        glfw.init()
        self.__context = glfw.create_window(100, 100, 'w', None, None)
        self.__another = glfw.create_window(200, 200, 'ww', None, None)

    def draw(self):
        while True:
            glfw.make_context_current(self.__context)
            print(mp.process.current_process(), 'draw')
            gl.glEnable(gl.GL_DEPTH_TEST)
            time.sleep(0.1)


MyManager.register('Window', Window)

if __name__ == '__main__':
    with MyManager() as manager:
        print(mp.process.current_process())
        w = manager.Window()
        w.draw()
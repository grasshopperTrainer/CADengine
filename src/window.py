from env import context

class Window:

    def __init__(self):
        context.My_glfw_gl.spec_check()


if __name__ == '__main__':
    win = Window()

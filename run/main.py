from UVT import Window, gl

class W(Window):
    def __init__(self):
        super().__init__(200, 200, 'window1')

    def draw(self):
        # print(self.current_window._context)
        print(gl.glGenBuffers(1))
        pass

w = W()
w.run(1)
print(w._context_manager._gl_logger._record)
print(w._context_manager._glfw_logger._record)
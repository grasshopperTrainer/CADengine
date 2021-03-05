from wkernel import Window


class MyWindow(Window):
    def __init__(self):
        super(MyWindow, self).__init__(500, 300, 'mywindow', None, None)
        self.framerate = 10

        self.devices.mouse.append_mouse_button_callback(self.button_callback)
        self.devices.mouse.append_cursor_enter_callback(self.enter_callback)
        self.devices.mouse.append_mouse_scroll_callback(self.wheel_callback)

    def draw(self):
        with self.devices.frames[0] as f:
            f.clear(1, 1, 1, 0)
            f.clear_depth()
        pass

    def button_callback(self, glfw_window, button, action, mods, mouse):
        print(button, action, mods, mouse)

    def enter_callback(self, glfw_window, entered, mouse):
        print(entered)

    def wheel_callback(self, glfw_window, xoffset, yoffset, mouse):
        print(xoffset, yoffset, mouse)


mw = MyWindow()
mw.run_all()

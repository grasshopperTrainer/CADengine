from wkernel import Window
from wkernel.MWindow import Window
from mkernel import Model
import gkernel.dtype.geometric as gt
import glfw

#
# class MainWindow(Window):
#     def __init__(self):
#         super().__init__(1000, 1000, 'mywindow')
#         print('MAIN DONE')
#         print()'
#
#     def draw(self):
#         print('drawing')

class MainWindow(Window):
    def __init__(self):
        super().__init__()
        pass


if __name__ == '__main__':
    window_main = MainWindow()
    window_main.run_all()

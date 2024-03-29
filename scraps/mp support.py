from wkernel import Window

from multiprocessing.managers import BaseManager


class MyManager(BaseManager):
    pass


mymanager = MyManager()


class MyWindow(Window):
    def __init__(self):
        super(MyWindow, self).__init__(500, 880, 'mywindow', None, None)
        self.framerate = 1

    def draw(self):
        print('drawing')


if __name__ == '__main__':

    MyManager.register('kkk', MyWindow)
    with MyManager() as manager:
        w = manager.kkk()
        w.run_all()
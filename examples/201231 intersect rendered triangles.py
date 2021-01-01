from wkernel import Window


class MyWindow(Window):
    def __init__(self):
        super().__init__(500, 500, 'my window 1', monitor=None, shared=None)
        self.framerate = 0.5

    def draw(self, frame_count=None):
        print('rendering')


MyWindow().run()

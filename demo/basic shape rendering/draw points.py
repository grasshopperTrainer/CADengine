from mkernel import AModeler
from wkernel import Window
import random


class MyWindow(Window):
    def __init__(self):
        super().__init__(500, 1000, 'my window 1', monitor=None, shared=None)
        self.framerate = 60

        # setup dolly
        d = self.devices.cameras.attach_fps_dolly(0, 0)
        d.move_boost = 5
        d.move_spd = 50

        # model for drawing
        self.modeler = AModeler()
        self.model = self.modeler.add_model(None)
        self.pnt_count = 0

    def draw(self, frame_count=None):
        if self.pnt_count < 100_000_000 and self.framerate % 10 == 0:
            p = self.modeler.add_pnt(self.model, *(random.randint(-10000, 10000) for _ in range(3)))
            p.frm = random.choice(('t', 'c', 's'))
            p.dia = random.randint(10, 100)
            self.pnt_count += 1

        with self.devices.panes[0] as p:
            p.clear(.1, .1, .1, 1)
            with self.devices.cameras[0]:
                self.modeler.render()

MyWindow().run_all()

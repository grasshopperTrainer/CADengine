from UVT import Window, DrawBit


class C(DrawBit):
    def draw(self):
        print('i am a child')
        super().draw()


class CC(DrawBit):
    def draw(self):
        print('i am a child of child')


w = Window(200, 200, 'window1', None, None)

c = C()
w.ftree_append_children(c)
cc = CC()
cc.ftree_set_parent(c)

w.run()

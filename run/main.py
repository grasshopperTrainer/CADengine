from UVT import Window

window1 = Window.new_window(200,200,'first window', monitor=None, shared=None)
window2 = Window.new_window(1000,1000, 'second window', monitor=None, shared=window1)
Window.run()
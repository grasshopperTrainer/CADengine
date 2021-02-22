import multiprocessing as mp
import glfw


class MW:
    def __init__(self, name):
        self.__glfw_window = glfw.create_window(100, 100, 'hey', None, None)
        # d[name] = 'self'
        # print(d)


def c(name):
    glfw.init()
    w = MW(name)

class Window:
    def __init__(self):
        m = mp.Manager()
        d = m.dict()
        self.__process = [mp.Process(target=c, args=(i, )) for i in range(2)]

    def run_all(self):


        for i in self.__process:
            # i.daemon = True
            i.start()

# print(d)

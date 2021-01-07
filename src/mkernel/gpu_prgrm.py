
class GPUPrgrm:

    def __init__(self, vrtx, frgm):
        """
        :param vrtx: vertex shader source file path
        :param frgm: fragment shader source file path
        """
        self.__prgrm = None

        self.__vrtx_file_path = vrtx
        self.__frgm_file_path = frgm
        # others to be included in future

    def __create_prgrm(self):
        """
        create program

        :return:
        """
        pass

    def __compile(self):
        """
        compile shaders

        :return:
        """
    def __checkbuild_prgrm(self):
        """
        lazy initialization: create program

        :return:
        """
        if self.__prgrm is None:
            self.__create_prgrm()

    def run(self):
        """
        executes gpu program

        used gpu buffer has to be bound beforehand
        this is a good place for lazy initialization as it is assumed
        caller is correctly binding OpenGL context
        :return:
        """
        self.__checkbuild_prgrm()

        print('run')
        pass
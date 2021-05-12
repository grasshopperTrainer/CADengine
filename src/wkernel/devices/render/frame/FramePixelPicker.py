import weakref as wr


class FramePixelPicker:
    """
    Wrap frame and texture id to be picked
    """

    def __init__(self, frame, attachment_id):
        self.__frame = wr.ref(frame)
        self.__aid = attachment_id

    def pick(self, pos, size):
        """
        :param pos:
        :param size:
        :return:
        """
        f = self.__frame()
        if f is not None:
            with f:
                return f.pick_pixels(self.__aid, pos, size)
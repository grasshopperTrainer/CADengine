import os
import multiprocessing
import cv2
from global_tools.singleton import Singleton


def _mp_export(file_name, texture):
    """
    actual runner for multiprocessing

    :return:
    """
    cv2.imwrite(file_name, texture)


@Singleton
class TxtrExporter:
    def __init__(self):
        self.__pool = multiprocessing.Pool()

    def export(self, texture, file_name: str):
        """
        export image in multiprocessing

        :param texture: numpy.ndarray, pixel data
        :param file_name:
        :return:
        """
        self.__pool.apply_async(_mp_export, args=(texture, file_name))
import heapq
from ..MVC import View
import weakref as wr
from collections import namedtuple
from my_patterns import FamilyMember
import threading
import warnings
import numpy as np
from noding import *

class _RenderTargetMember(FamilyMember):
    pass

class _RenderTargetPool(_RenderTargetMember):
    def __init__(self, window):
        super().__init__()
        self.fm_append_member(window, self)
        self._current_stack = []

    def __getitem__(self, item):
        return self.fm_get_child(item)

    def append_new_target(self):
        raise NotImplementedError

    def current_target(self):
        if self._current_target:
            return self._current_stack[-1]
        return None


class _RenderTarget(_RenderTargetMember):

    def __enter__(self):
        self.fm_get_parent(0)._current_stack.append(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fm_get_parent(0)._current_stack.pop()


class Cameras(_RenderTargetPool):
    def __init__(self, window):
        super().__init__(window)
        self.append_new_target()

    def append_new_target(self):
        new_camera = FovCamera(50, 1, 1, 1000000)
        self.fm_append_member(self, new_camera)

class FovCamera(NodeBody):
    in0_hfov = Input()
    in1_ratio = Input()
    in2_near = Input()
    in3_far = Input()

    out0_left = Output()
    out1_right = Output()
    out2_bottom = Output()
    out3_top = Output()
    out4_near = Output()
    out5_far = Output()
    out6_hfov = Output()
    out7_vfov = Output()
    out8_ratio = Output()
    out9_proj_mat = Output()

    def calculate(self, hfov, ration, near, far):
        print()

    def __enter__(self):
        self.fm_get_parent(-1)._current_stack.append(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fm_get_parent(-1)._current_stack.pop()

    # @property
    # def properties(self):
    #     np = namedtuple('camera prop', ('left', 'right', 'bottom', 'top', 'near', 'far', 'hfov', 'vfov', 'ratio'))
    #     return np(self._l, self._r, self._b, self._t, self._n, self._f, self.hfov, self.vfov, self.ratio)
    #
    # @property
    # def hfov(self):
    #     return np.degrees(2*np.arcsin(self._r/np.sqrt(self._n**2 + self._r**2)))
    #
    # @property
    # def vfov(self):
    #     return np.degrees(2*np.arcsin(self._t/np.sqrt(self._n**2 + self._t**2)))
    #
    # @property
    # def ratio(self):
    #     return self._r/self._t
    #
    # @property
    # def proj_mat(self):
    #     """    #     return projection matrix.......
    #     :return:
    #     """
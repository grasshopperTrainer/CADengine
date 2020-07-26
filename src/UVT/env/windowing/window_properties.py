import heapq
from ..MVC import View
import weakref as wr
from collections import namedtuple
from my_patterns import FamilyMember
import threading


class _RenderTargetMember(FamilyMember):
    pass

class _RenderTargetPool(_RenderTargetMember):
    def __init__(self, window):
        super().__init__()
        self.fm_append_member(window, self)
        self._current_target = None

    def __getitem__(self, item):
        return self.fm_get_child(item)

    def append_new_target(self):
        raise NotImplementedError

class _RenderTarget(_RenderTargetMember):

    def __enter__(self):
        self.fm_get_parent(0)._current_target = self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fm_get_parent(0)._current_target = None

class Cameras(_RenderTargetPool):
    def __init__(self, window):
        super().__init__(window)
        self.append_new_target()

    def append_new_target(self):
        new_camera = Camera(-100,100,-100,100,0.1,100)
        self.fm_append_member(self, new_camera)


class Camera(_RenderTarget):
    def __init__(self, left, right, bottom, top, near, far):
        super().__init__()
        self._l = left
        self._r = right
        self._b = bottom
        self._t = top
        self._n = near
        self._f = far


#
# class _RenderTarget:
#     def __str__(self):
#         return f"< {type(self).__name__} : {self.properties} >"
#
# class _TargetView(_RenderTarget, View):
#     """
#     Viewport to render on
#     """
#
#     @property
#     def properties(self):
#         return namedtuple('target_view', ('x', 'y', 'w', 'h'))(self.x, self.y, self.w, self.h)
#
#     def __lt__(self, other):
#         """
#         No order in viewports
#         :param other:
#         :return:
#         """
#         if not isinstance(other, _TargetView):
#             raise TypeError
#         return True
#
#
# class _TargetCamera(_RenderTarget):
#     pass
#
#     @property
#     def properties(self):
#         return ''
#
# class _TargetLayer(_RenderTarget):
#     def __init__(self, idx):
#         self._idx = idx
#
#     @property
#     def properties(self):
#         return namedtuple('target_layer', ('idx'))(self._idx)
#
#     def __lt__(self, other):
#         if not isinstance(other, _TargetLayer):
#             raise TypeError
#         return self._idx < other._idx
#
#
# class _RenderTargetPool:
#     def __init__(self, window):
#         self._window = wr.ref(window)
#
#         self._sorted = False
#         self._iter_count = 0
#         self._pool = []
#
#     def append(self):
#         raise NotImplementedError
#
#     def __getitem__(self, item):
#         return self._pool[item]
#
#     def __iter__(self):
#         if not self._sorted:
#             self._pool.sort()
#             self._sorted = True
#
#         self._iter_count = 0
#         return self
#
#     def __next__(self):
#         if self._iter_count >= len(self._pool):
#             raise StopIteration
#         o = self._pool[self._iter_count]
#         self._iter_count += 1
#         return o
#
#     @property
#     def win(self):
#         return self._window()
#
#
# class _Views(_RenderTargetPool):
#     def __init__(self, window):
#         super().__init__(window)
#         self.append(0, 0, 1.0, 1.0)
#
#     def append(self, x, y, w, h):
#         self._pool.append(_TargetView(x, y, w, h, self.win))
#         self._sorted = False
#
#
# class _Cameras(_RenderTargetPool):
#     def __init__(self, window):
#         super().__init__(window)
#         self.append()
#
#     def append(self):
#         self._pool.append(_TargetCamera())
#         self._sorted = False
#
#
# class _Layers(_RenderTargetPool):
#     def __init__(self, window):
#         super().__init__(window)
#         self.append(0)
#
#     def append(self, idx):
#         self._pool.append(_TargetLayer(idx))
#         self._sorted = False
#
# class RenderRegistry:
#     def __init__(self, window):
#         self._window = wr.ref(window)
#
#         self._layers = _Layers(window)
#         self._views = _Views(window)
#         self._cameras = _Cameras(window)
#
#         self._render_que = {}
#
#     def _register(self, lyr=None, viw=None, cam=None):
#         """
#         Register render function call
#         :param lyr: layer to draw on
#         :param viw: view to draw on
#         :param cam: camera to draw with
#         :return:
#         """
#         # value, type check
#         lyr = self._layers[0] if lyr is None else lyr
#         viw = self._views[0] if viw is None else viw
#         cam = self._cameras[0] if cam is None else cam
#         for v, t in zip((lyr, viw, cam), (_TargetLayer, _TargetView, _TargetCamera)):
#             if not isinstance(v, t):
#                 raise TypeError(v, t)
#
#         # wrapper for decoration
#         def _wrapper(fnc):
#             # register in assigned order
#             self._render_que.setdefault(lyr, {}).setdefault(viw, {}).setdefault(cam, []).append(fnc)
#         return _wrapper
#
#     @property
#     def win(self):
#         return self._window()
#
#     def _render(self):
#         self.win.gl.glEnable(self.win.gl.GL_SCISSOR_TEST)
#
#         self.win.gl.glClear(self.win.gl.GL_COLOR_BUFFER_BIT)
#         for lyr in self._layers:
#             views = self._render_que.get(lyr, {})
#
#             for viw in self._views:
#                 cameras = views.get(viw, {})
#                 if cameras:
#                     self.win.gl.glViewport(*viw.properties)
#                     self.win.gl.glScissor(*viw.properties)
#
#                 for cam in self._cameras:
#                     for fnc in cameras.get(cam, []):
#                         fnc()
#
#         self.win.gl.glDisable(self.win.gl.GL_SCISSOR_TEST)
#

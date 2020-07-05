import heapq
from ..MVC import View
import weakref as wr
from collections import namedtuple


class _RenderTarget:
    def __str__(self):
        return f"< {type(self).__name__} : {self.properties} >"

class _TargetView(_RenderTarget, View):
    def __init__(self, x, y, w, h, mother):
        super().__init__(mother)
        self._x = x
        self._y = y
        self._w = w
        self._h = h

    @property
    def properties(self):
        return namedtuple('target_view', ('x', 'y', 'w', 'h'))(self._x, self._y, self._w, self._h)

class _TargetCamera(_RenderTarget):
    pass

    @property
    def properties(self):
        return ''

class _TargetLayer(_RenderTarget):
    def __init__(self, idx):
        self._idx = idx

    def __gt__(self, other):
        if not isinstance(other, _TargetLayer):
            raise TypeError
        return self._idx < other._idx

    @property
    def properties(self):
        return namedtuple('target_layer', ('idx'))(self._idx)

    def __lt__(self, other):
        if not isinstance(other, _TargetLayer):
            raise TypeError
        return self._idx < other._idx


class _RenderTargetPool:
    def __init__(self, window):
        self._window = wr.ref(window)

        self._sorted = False
        self._iter_count = 0
        self._pool = []

    def append(self):
        raise NotImplementedError

    def __getitem__(self, item):
        return self._pool[item]

    def __iter__(self):
        if not self._sorted:
            self._pool.sort()
            self._sorted = True

        self._iter_count = 0
        return self

    def __next__(self):
        if self._iter_count >= len(self._pool):
            raise StopIteration
        o = self._pool[self._iter_count]
        self._iter_count += 1
        return o

    @property
    def win(self):
        return self._window()


class _Views(_RenderTargetPool):
    def __init__(self, window):
        super().__init__(window)
        self.append(0, 0, 1.0, 1.0)

    def append(self, x, y, w, h):
        self._pool.append(_TargetView(x, y, w, h, self.win))
        self._sorted = False


class _Cameras(_RenderTargetPool):
    def __init__(self, window):
        super().__init__(window)
        self.append()

    def append(self):
        self._pool.append(_TargetCamera())
        self._sorted = False


class _Layers(_RenderTargetPool):
    def __init__(self, window):
        super().__init__(window)
        self.append(0)

    def append(self, idx):
        self._pool.append(_TargetLayer(idx))
        self._sorted = False

class RenderRegistry:
    def __init__(self, window):
        self._window = wr.ref(window)

        self._views = _Views(window)
        self._cameras = _Cameras(window)
        self._layers = _Layers(window)

        self._render_que = {}

    def _register(self, lyr=None, viw=None, cam=None):
        lyr = self._layers[0] if lyr is None else lyr
        viw = self._views[0] if viw is None else viw
        cam = self._cameras[0] if cam is None else cam
        for i in (lyr, viw, cam):
            if not isinstance(i, _RenderTarget):
                raise TypeError

        def _wrapper(fnc):
            # register in order
            self._render_que.setdefault(lyr, {}).setdefault(viw, {}).setdefault(cam, []).append(fnc)
        return _wrapper

    def _render(self):
        for lyr in self._layers:
            views = self._render_que.get(lyr, {})
            for viw in self._views:
                cameras = views.get(viw, {})
                for cam in self._cameras:
                    for fnc in cameras.get(cam, []):
                        fnc()


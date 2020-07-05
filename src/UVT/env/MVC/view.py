import weakref as wr


class View:
    def __init__(self, x, y, w, h, mother):
        if mother is None:
            self._mother = None
        elif isinstance(mother, View):
            self._mother = wr.ref(mother)
        else:
            raise TypeError

        for n, v in zip(('x', 'y', 'w', 'h'),  (x, y, w, h)):
            self._init_attr(n, v)

    @property
    def mother(self):
        if self._mother is None:
            return None
        return self._mother()

    def _init_attr(self, attr_name, value):
        if isinstance(value, (list, tuple)):
            setattr(self, attr_name, value[0])
            setattr(self, f"_{attr_name}_def", value[1])
        elif isinstance(value, (int, float, callable)):
            setattr(self, attr_name, value[0])
            setattr(self, f"_{attr_name}_def", 0)

    def _evaluator(self, attr_name):
        attr = getattr(self, f"_{attr_name}")

        if isinstance(attr, int):
            return attr
        elif isinstance(attr, float):
            if self.mother is None:
                return getattr(self, f"_{attr_name}_def") * attr
            else:
                return getattr(self.mother, attr_name) * attr
        elif isinstance(attr, callable):
            if self.mother is None:
                return attr(getattr(self, f"_{attr_name}_def"))
            else:
                return attr(getattr(self.mother, attr_name))
        else:
            raise NotImplementedError

    @property
    def x(self):
        return self._evaluator('x')

    @property
    def y(self):
        return self._evaluator('y')

    @property
    def w(self):
        return self._evaluator('w')

    @property
    def h(self):
        return self._evaluator('h')


if __name__ == '__main__':
    v = View(1, 2, 0.5, lambda y: y - 10, mother=None)
    print(v.x)

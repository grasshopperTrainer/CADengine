from collections import deque
import heapq
import inspect

import components as comp

class Relationship:
    """
    Relationship between two components
    """
    def __init__(self, left, outp, inp, right):
        if not hasattr(left, outp):
            raise AttributeError(f"component {left} has no such output {outp}")
        if not hasattr(right, inp):
            raise AttributeError(f"component {right} has no such input {inp}")

        self._left = left
        self._outp = outp
        self._inp = inp
        self._right = right

    def push_rightward(self):
        """
        Push left's output into right's input
        :return:
        """
        # but how?
        self._right.__setattr__(self._inp, self._left.__getattribute__(self._outp))

    @property
    def right(self):
        return self._right
    @property
    def left(self):
        return self._left

class Pipeline:
    """
    Chain of operations

    built by components and relationships between them
    """
    render_window = comp.Input('render_window')

    def __init__(self, render_window=None):
        if render_window is not None:
            self.render_window = comp.Window(render_window)
        else:
            self.render_window = None

        self._components = set()
        self._rels = {}
        self._ends = set(), set()   # left right ends

    def register(self, comp):
        """
        Make component visible by pipeline
        :param comp:
        :return:
        """
        self._components.add(comp)

    def relate(self, left, outp, inp, right):
        """
        Build relationship between two components via output and input interface

        Think of a line connecting two functions from left to right.
        :param left: component evaluated before
        :param outp: output of left
        :param inp: input of right
        :param right: component evaluated latter
        :return:
        """
        self._rels.setdefault(left, []).append(Relationship(left, outp, inp, right))
        # see if components are at ends
        if left not in self._components:
            self.register(left)
            self._ends[0].add(left)
        elif left in self._ends[1]:
            self._ends[1].remove(left)

        if right not in self._components:
            self.register(right)
            self._ends[1].add(right)
        elif right in self._ends[0]:
            self._ends[0].remove(right)

    def eval_hierarchy(self):
        """
        Align components from left to right

        So that all components can have updated inputs.
        :return: ((component, depth), ...)
        """
        # temporarily full build only
        record = {comp: 0 for comp in self._components}

        entry = len(self._ends[0])  # not to compare components, need unique id
        comps = [(0, i, comp) for i, comp in enumerate(self._ends[0])]
        heapq.heapify(comps)

        while comps:
            depth, _, comp = heapq.heappop(comps)
            if depth < record[comp]:    # there is a longer path
                continue

            for rel in self._rels.get(comp, []):
                if depth+1 > record[rel.right]:   # looking for longest path
                    record[rel.right] = depth + 1
                    heapq.heappush(comps, (depth+1, entry, rel.right))
                    entry += 1

        return sorted(record.items(), key=lambda x: x[1])

    def calc(self):
        """
        Calculate by passing values incrementally

        :return:
        """
        for comp, depth in self.eval_hierarchy():
            # calculate using current inputs
            comp.operate()
            # update outputs to related right components
            for r in self._rels.get(comp, []):
                r.push_rightward()


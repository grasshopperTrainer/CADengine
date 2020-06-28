import weakref as wr
from collections import namedtuple, deque
import inspect
import warnings
import heapq


class NodeSpvr:
    """
    Supervisor of nodes

    Stores relationship and hierarchy between nodes
    Only cares relationship between
    """

    def __init__(self, inst):
        self._graph = {}
        self._needto_update = wr.WeakSet()

        self._graph[inst] = {'dist':0, 'rels':{}}
        self._needto_update.add(inst)

    def _relate(self, this_node, out, inp, right_node):
        """
        Write down relationship

        Literally imagine two nodes connected by a line,
        of which two ends from left to right are the output and the input of two nodes.
        :param this_node:
        :param out:
        :param inp:
        :param right_node:
        :return:
        """
        self.rels(this_node).setdefault(out, {}).setdefault(right_node, set()).add(inp)

    def build_rel(self, out, inp):
        """
        Build relationship between two nods via interfaces

        :param out:
        :param inp:
        :return:
        """
        if out.intf_holder._node_spvr != self:
            raise AttributeError
        l_supv, r_supv = out.intf_holder._node_spvr, inp.intf_holder._node_spvr
        # two graphs are islands so need to be merged beforehand
        is_merged = False
        if l_supv != r_supv:
            # simply update dict and assign new supervisor to instances(nodes)
            l_supv._graph.update(r_supv._graph)
            for node in r_supv._graph:
                node._node_spvr = l_supv
            is_merged = True

        # check distance and update if needed
        l_node, r_node = out.intf_holder, inp.intf_holder

        # loop check ?
        # check only relationships is being built within an island
        # and right is before left
        if not is_merged:
            for nxt_node in self._node_rightward(r_node):
                if nxt_node == l_node:
                    warnings.warn("Trying to make a look. Connection not accepted")
                    return
                if self.dist(nxt_node) > self.dist(l_node):
                    break

        # write relationship and calculate distance,
        # push value, push r_node to update que as new value has been just pushed
        self._relate(l_node, out, inp, r_node)
        self._graph[r_node]['dist'] = self.dist(l_node) + 1
        inp._intf_obj = out._intf_obj
        self.push_needto_update(r_node)

        # update distance of all r_node's rightward
        # no need to align nodes. just que
        que = deque([r_node])

        while que:
            node = que.popleft()
            this_dist = self.dist(node)
            for _, rights in self.rels(node).items():
                for right in rights:
                    that_dist = self.dist(right)
                    if this_dist >= that_dist:
                        self._graph[right]['dist'] = this_dist + 1
                        que.append(right)

    def disconnect(self, instance, intf):
        """
        Remove all connections of which one end is given interface
        :param instance:
        :param intf:
        :return:
        """
        # !Q does disconnection affect dist of nodes?
        # it doesn't violate hierarchy but could be cleaned to maintain dist understandable?
        # TODO: algorithm for maintaining nodes' (attr) dist relatively close
        if intf.intf_sign == Input:
            for node, rels in self._graph.items():
                for out, rights in rels.items():
                    for right, inps in rights.items():
                        if intf in inps:
                            inps.remove(intf)
                            break

        elif intf.intf_sign == Output:
            d = self.rels(instance)
            if intf in d:
                for right, inps in d.items():
                    for inp in inps:
                        delattr(right, inp)
                del d[intf]
        else:
            NotImplementedError
        self.push_needto_update(instance)

    def push_needto_update(self, instance):
        """
        Push into need to upadate que

        Needing to update means node's (def) operate has to executed to update output value.
        :param instance:
        :return:
        """
        self._needto_update.add(instance)

    def dist(self, node):
        """
        Hierarchial identifier

        Closer to 0 means it has to be calculated beforehand.
        Higher means it has to be calculated later.
        :param node:
        :return:
        """
        return self._graph[node]['dist']

    def rels(self, node):
        """
        Return info dict describing rightward nodes of this node
        :param node:
        :return:
        """
        return self._graph[node]['rels']

    def update_rightward(self, end_node=None):
        """
        Build update graph then push values consequently

        From update_que, find all nodes needing update in rightward order
        then for each execute (def) operate and push outputs rightward
        :return:
        """
        # adding i for dist(n) being the same
        # !Q is _update_que node that has run (def) operate or that has to run operate?
        for nxt_node in self._node_rightward(self._needto_update):
            if nxt_node in self._needto_update: # reset que
                self._needto_update.remove(nxt_node)

            nxt_node.operate()  # run to update outputs
            # push outputs to next node
            for out, rights in self.rels(nxt_node).items():
                for right, inps in rights:
                    for inp in inps:
                        inp._intf_obj = out._intf_obj

            if nxt_node == end_node:
                # push next of nxt_node needto update and stop updating
                for out, rights in self.rels(nxt_node):
                    self._needto_update.update(rights.keys())

    def _node_rightward(self, nodes):
        if isinstance(nodes, (list, tuple, set)):
            heap = list([(self.dist(n), i, n) for i, n in enumerate(nodes)])
            entry = len(nodes)
            visited = set(nodes)
        else:
            heap = [(self.dist(nodes), 0, nodes)]
            entry = 1
            visited = {nodes}

        heapq.heapify(heap)
        while heap:
            dist, _, node = heapq.heappop(heap)
            yield node
            for out, rights in self.rels(node).items():
                for right, ins in rights.items():
                    if right not in visited:
                        heapq.heappush(heap, (self.dist(right), entry, right))
                        visited.add(right)
                        entry += 1

    def __len__(self):
        return len(self._graph)


class IntfObj:
    """
    Wrapper storing additional properties to wrapped type

    From interface's view, instance of this is not assigned to another or removed until
    the intf is __delete__ -> meaning resetting to default value.
    """

    def __init__(self, instance, name, sign, value):
        """
        Store interface properties
        :param instance:
        :param name:
        :param sign:
        :param value:
        :return:
        """
        self._intf_holder = wr.ref(instance)
        self._intf_is_deleted = False
        self._intf_name = name
        self._intf_sign = sign
        self._intf_obj = value  # real value wrapped

    def __str__(self):
        return f"< {self._intf_sign.__name__} : {self._intf_obj} >"

    @property
    def intf_name(self):
        return self._intf_name

    @property
    def intf_holder(self):
        ins = self._intf_holder()
        if ins is None:
            raise NotImplementedError
        return ins

    @property
    def intf_sign(self):
        return self._intf_sign

    @property
    def intf_is_deleted(self):
        return self._intf_is_deleted

    @property
    def real_value(self):
        return self._intf_obj

    def __add__(self, other):
        return self.real_value.__add__(other)

    def __sub__(self, other):
        return self.real_value.__sub__(other)

    def __truediv__(self, other):
        return self.real_value.__truediv__(other)

    def __floordiv__(self, other):
        return self.real_value.__floordiv__(other)

    def __mul__(self, other):
        return self.real_value.__mul__(other)


class IntfDescriptor:
    """
    Interface node for input and output

    To control setting value
    """
    _sign = None

    def __init__(self, name, def_val):
        self._name = name
        self._record_name = f'_{self._sign}_{name}'
        self._def_val = def_val

    def __set__(self, instance, value):
        """
        !!! only input triggers (def) push to update que

        :param instance:
        :param value:
        :return:
        """


    def __get__(self, instance, owner) -> IntfObj:
        """
        Getting input value

        !!! Getting input and output triggers (def) update
        1. make value up-to-date by telling node supervisor to update
        2. return intf value

        :param instance:
        :param owner:
        :return:
        """
        self._init_interface(instance)
        instance._node_spvr.update_rightward(instance)
        return getattr(instance, self._record_name)

    def __delete__(self, instance):
        """
        Disconnection from output

        1. Remove connection in node graph
        2. Reset with default value

        :param instance:
        :return:
        """
        self._init_interface(instance)
        instance._node_spvr.disconnect(instance, getattr(instance, self._record_name))
        intf_obj = IntfObj(instance, self._name, type(self), self._def_val)
        setattr(instance, self._record_name, intf_obj)

    def _init_interface(self, instance):
        """
        Initiate interface

        1. add attribute into the instance
        2. add signature's attribute set, e.g. _inputs, into the instance
        3. add node grapher to the instance
        :param instance:
        :return:
        """
        # add attriute
        if not hasattr(instance, self._record_name):
            # 1 use default value if there isn't one
            intf_obj = IntfObj(instance, self._name, type(self), self._def_val)
            setattr(instance, self._record_name, intf_obj)
            # 2 collect instance attr_name, then set with sign
            inst_dict = instance.__dict__.setdefault('_intfs', {})
            inst_dict.setdefault(self, set()).add(self._record_name)
        # 3 add node grapher if there isn't
        if not hasattr(instance, '_node_spvr'):
            setattr(instance, '_node_spvr', NodeSpvr(instance))


class Input(IntfDescriptor):
    """
    Designate input value
    """
    _sign = 'input'

    def __set__(self, instance, value):
        """
        Handles assigning python primitive to InterfaceValueContainer

        :param instance:
        :param value:
        :return:
        """
        self._init_interface(instance)

        if isinstance(value, IntfObj):  # if connecting node to node
            if value.intf_sign == Input: # if connecting input -> input interfaces
                raise AttributeError("direction should be (output) -> (input)")
            instance._node_spvr.build_rel(value, getattr(instance, self._record_name))

        else:  # if putting raw value
            self.__delete__(instance)   # existing connection has to be removed as this is explicit __set__
            getattr(instance, self._record_name)._intf_obj = value


class Output(IntfDescriptor):
    """
    Output Interface

    Manages setting getting deleting output value
    """
    _sign = 'output'

    def __set__(self, instance, value):
        """
        Sets output value

        Only one case is accepted :
        Instance's internal operation trying to set value to the output
        else, output value of node is not allowed to be set as it's always the result of the node's (def) operate.
        And as (def) operate will only be run by (obj) _node_spvr, there is no need to set rightward to be updated.

        :param instance: Node
        :param value:
        :return:
        """
        self._init_interface(instance)
        # guess if assigning value is called inside the node
        calling_frame = inspect.currentframe().f_back
        frameinfo = inspect.getframeinfo(calling_frame)
        local_attr = inspect.getargvalues(calling_frame).locals
        # 3 guesses:
        # guess if the node has attribute named of function setting value in
        # guess if that attribute is a method
        # guess if 'self' is in local arg and is the node
        if hasattr(instance, frameinfo.function):
            if inspect.ismethod(getattr(instance, frameinfo.function)):
                if 'self' in local_attr and local_attr['self'] == instance:
                    value = value.real_value if isinstance(value, IntfObj) else value
                    getattr(instance, self._record_name)._intf_obj = value
                    # if node's output is updated, right of it has to have values in and set to update
                    # pushing is needed for the case (def) operate is executed explicitly?
                    # or can't it be executed that way? -> it can't i suppose
                    # instance._node_spvr.push_rightward_update_que(instance, getattr(instance, self._record_name))
                    return
        raise AttributeError("Output can't be set explicitly")


class K:
    def __init__(self, a, b):
        self.a = a
        self.b = b


class A:
    a = Input('a', 0)
    a_out = Output('a_out', 0)

    def operate(self):
        self.a_out = self.a
        print('operation A')


class B:
    b = Input('b', 0)
    c = Output('c', 0)

    def operate(self):
        self.c = self.b * 2
        print('operation B')


if __name__ == '__main__':
    def simple_task():
        a = A()
        b = B()
        print('setting value explicitly')
        a.a = 10
        print(a.a)
        print(a.a_out)
        print(a.a_out)
        # setting reverse
        # a.a_out = b.b

        print('simple connection')
        b.b = a.a_out
        print(b.b)
        print('check operation')
        print(b.c)
        print('check if operation is not called when no change made')
        print(b.c)
        print(b.b)
        print('check update chained')
        a.a = 15
        print(b.b)
        print(b.c)
        print('check disconnection from input')
        del b.b
        print(a.a)
        print(a.a_out)
        print(b.c)
        print('check disconnection from output')
        a.a = 100
        b.b = a.a_out
        print(b.c)
        del a.a_out
        print()
        print(a.a_out)
        print(b.c)

    def three_node():
        class A:
            i = Input('i', None)
            o = Output('o', None)

            def operate(self):
                print('Operate A')
                self.o = self.i

        class B:
            i = Input('i', None)
            o = Output('o', None)

            def operate(self):
                print('Operate B')
                self.o = self.i

        class C:
            i = Input('i', None)
            o = Output('o', None)

            def operate(self):
                print('Operate C')
                self.o = self.i

        a, b, c = A(), B(), C()
        c.i = b.o
        b.i = a.o
        a.i = 10
        print(c.o)
        a.i = 20
        print(c.o)

    def rebuild():
        class A:
            i = Input('i', 0)
            o = Output('o', None)

            def operate(self):
                print('operating A')
                self.o = self.i + 1

        a = A()
        print('input of a', a.i, a._node_spvr)
        print('Output of a', a.o)
        del a.o
        b = A()
        b.i = a.o

        # print('Output of a', a.o)
        # b = A()
        # print('connect')
        # b.i = a.o
        # print(a._node_spvr._graph)
        # print()
        # print('new value set')
        # a.i = 20
        # # print(a._node_spvr, b._node_spvr)
        # # print(a._node_spvr._update_que)
        # print('--------------------')
        # print(b._node_spvr._graph)
        # print(b.o)
        # b.i = 100
        # print(b.o)
        # print(a.i, a.o, b.i, b.o)
        # b.i = a.o
        # a.i = 1000
        # print(a.i, a.o, b.i, b.o)
        # print(a._node_spvr._update_que)
        # print(b._node_spvr._update_que)
        # print(b.i, b._node_spvr._update_que)
        # print(a._node_spvr, b._node_spvr)
        # print(b._node_spvr._graph)
        # a.i = 10
        # print(b.o)
        # c = A()
        # c.i = b.o
        # print(c.i, c.o)



    rebuild()
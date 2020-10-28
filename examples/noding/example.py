from JINTFP import NodeBody, Input, Output


class MyNode(NodeBody):
    # input descr. will only accept instance of `typs`
    in0 = Input(def_val='', typs=str)
    in1 = Input(def_val='', typs=str)

    out = Output()

    def __init__(self, id):
        # NodeBody's `__init__` has to be called
        # to initiate instance as a Node
        super().__init__()
        self._do_upper = False
        self._id = id

    def calculate(self, in0, in1):
        # user should provide matching number of
        # attribute to use them in calculation
        print(f'RUNNING Node : {self._id}')
        if self._do_upper:
            return (in0 + in1).upper()
        return in0 + in1

    def set_upper(self):
        # except inheriting and initiating,
        # concrete Node acts the same as any other class
        # user can extend its functionality as they wish to
        self._do_upper = True
        # reset to be recalculated with cached value
        self.reset_downstream()

node0 = MyNode(0)
node1 = MyNode(1)
node2 = MyNode(2)
print('>>> building graph')
node2.in0 = node0.out
node2.in1 = node1.out

print('>>> building graph more')
node3, node4 = MyNode(3), MyNode(4)
node3.in0, node3.in1 = node2.out, node1.out
node0.in0 = node4.out
# feeding inputs
node4.in0, node4.in1 = 'x', 'y'
node0.in1 = 'a'
node1.in0, node1.in1 = 'm', 'n'
print('\n>>> getting outputs')
print(node3.out, node4.out)

...
print('>>> tweaking calculation')
node0.set_upper()
print('>>> getting unaffected')
print(node1.out)
print('>>> getting affected')
print(node3.out)
...
print('>>> getting real value')
print(node3.out.r, type(node3.out.r))
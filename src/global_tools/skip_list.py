import random
from math import inf


class SkipList:
    def __init__(self, key_provider=None):
        """

        :param key_provider: function, lambda, that extracts key for comparison
                            if not provided, value's magic method will be used
        """
        if key_provider is not None and not callable(key_provider):
            raise TypeError
        self.__key_provider = (lambda x: x) if key_provider is None else key_provider

        self.__head = self.__HeadNode()
        self.__tail = self.__TailNode()
        self.__head.set_right(level=0, node=self.__tail, width=1)
        self.__size = 0

    def __contains__(self, item):
        """
        membership test

        ! this method test instance equality not logical
        :param item: item to search for
        :return:
        """
        node = self.__search_bisect_left(item, return_path=False)
        for nn, _ in node.iter_level(level=0):
            if self.__key_provider(nn.val) <= self.__key_provider(item):
                if nn.val is item:
                    return True
            else:
                return False
        return False

    def __len__(self):
        return self.__size

    def __getitem__(self, item):
        """
        binary searching by width

        1. move right untile steps are too big
        2. go down
        3. repeat from 1
        :param item:
        :return:
        """
        if item < -len(self) or len(self) <= item:
            raise IndexError

        if item < 0:
            item += len(self)

        level = self.__head.num_levels - 1
        node = self.__head
        steps = 0
        while True:
            while steps + node.get_right(level)[1] <= item+1:
                node, width = node.get_right(level)
                steps += width
            if steps == item+1:
                return node.val
            level -= 1

    def __str__(self):
        return f"<SkipList: s,l = {self.__size},{self.__head.num_levels}>"

    @property
    def num_levels(self):
        return self.__head.num_levels

    def push(self, val):
        """
        insert new value

        :param val:
        :return:
        """
        cnode = self.__Node(val)
        node_steps = self.__search_bisect_right(val, return_path=True)
        summed_step = 1
        for level in range(self.num_levels):
            # stop growing if coil flip fails, but dont consider for a base level
            if level != 0 and not self.__flip_coin():
                # update width by +1 for levels above as new value has been inserted in between
                for lev in range(level, self.num_levels):
                    lnode, _ = node_steps.pop()
                    rnode, width = lnode.get_right(level=lev)
                    lnode.set_right(level=lev, node=rnode, width=width + 1)
                break
            lnode, step = node_steps.pop()
            # grow in level
            twidth = lnode.get_right(level)[1] + 1  # total width +1 for inserting new
            lwidth = summed_step                    # left width equals to summed steps
            rwidth = twidth - lwidth                # right width is rest of twidth
            # linked list insertion
            rnode = lnode.get_right(level)[0]
            cnode.set_right(level, rnode, rwidth)
            lnode.set_right(level, cnode, lwidth)
            summed_step += step                     # update steps
        # target node topped existing level if all coin flip succeeded.
        # add new level -> but why is this needed?
        else:
            # new width is +1 of total size for insertion and +1 for logical consistency
            self.__head.set_right(level=self.__head.num_levels, node=self.__tail, width=self.__size+2)
        # mark size growth
        self.__size += 1

    def remove(self, val):
        """
        remove given value in list

        :param val: value in list
        :return:
        """
        lnodes = self.__search_bisect_left(val, return_path=True)
        # step right has to be the value
        tnode = lnodes[-1][0].get_right(level=0)[0]  # target node
        if tnode.val != val or tnode is self.__tail:
            raise ValueError('given value doesnt exist')
        self.__remove_right(lnodes)

    def __remove_right(self, path_nodes):
        """
        remove right value of given search path

        1. linked list relinking and update width
        2. update width at higher level
        3. truncate redundant levels
        :param path_nodes:
        :return:
        """
        tnode = path_nodes[-1][0].get_right(level=0)[0]
        # linked list relink all
        for level in range(tnode.num_levels):
            lnode, _ = path_nodes.pop()  # backward
            _, lwidth = lnode.get_right(level)
            rnode, rwidth = tnode.get_right(level)
            lnode.set_right(level, node=rnode, width=lwidth + rwidth - 1)  # width-1 for removal
        # update width above
        for level in range(tnode.num_levels, self.num_levels):
            lnode, _ = path_nodes.pop()
            rnode, width = lnode.get_right(level)
            lnode.set_right(level, node=rnode, width=width - 1)  # width-1 for removal
        # truncate redundant level
        level = self.num_levels - 1
        while level != 0 and self.__head.get_right(level - 1)[0] == self.__tail:
            self.__head.pop_level()
            level -= 1
        # update remnant
        tnode.delete()
        self.__size -= 1

    def remove_all(self, val):
        """
        remove all logically equal values

        :param val:
        :return:
        """
        raise NotImplementedError

    def pop(self):
        """
        pop last

        ? need better implementation?
        :return:
        """
        search_path = self.__search_idx(-2)
        result = search_path[-1][0].get_right(level=0)[0].val
        self.__remove_right(search_path)
        return result

    def has_value(self, val):
        """
        check if logically equal value exists in the list

        ! this is different from membership testing(~ in Skiplist())
        :param val: value to check
        :return: bool
        """
        searched = self.__search_bisect_right(val, return_path=False)
        return self.__key_provider(val) == self.__key_provider(searched)

    def __flip_coin(self):
        """
        1/2 probability coin flip

        :return: bool
        """
        return bool(random.getrandbits(1))

    def __search_idx(self, idx):
        """
        search node path of given value

        :param idx: node path at each level, node of 0 idx is the highest
        :return:
        """
        if idx < -len(self)-1 or len(self) <= idx:  # allow -1 for getting left of first?
            raise IndexError

        if idx < 0:
            idx += len(self)

        level = self.__head.num_levels - 1
        node = self.__head
        path_nodes = []
        sum_steps = 0
        while True:
            steps = 0
            while sum_steps + node.get_right(level)[1] <= idx+1:
                node, width = node.get_right(level)
                steps += width
                sum_steps += width
            path_nodes.append((node, sum_steps))
            if level != 0:
                level -= 1
            else:
                return path_nodes

    def __search_bisect_left(self, val, return_path):
        level = self.__head.num_levels - 1
        node = self.__head
        rightmosts = []
        while True:
            steps = 0
            # move right while target is bigger than current
            # <= to maintain insertion
            while True:
                rnode, width = node.get_right(level)
                if rnode == self.__tail:
                    break
                elif self.__key_provider(rnode.val) < self.__key_provider(val):
                    steps += width
                    node = rnode
                else:
                    break

            # check if currently at base level
            if return_path:
                rightmosts.append((node, steps))
            if level != 0:
                level -= 1
            else:
                if return_path:
                    return rightmosts
                else:
                    return node

    def __search_bisect_right(self, val, return_path):
        """
        search node path that leads to equal or less, rightmost, of given value

        :param val: list, rightmost nodes on each level
        :return:
        """
        level = self.__head.num_levels-1
        node = self.__head
        widths = []
        rightmosts = []
        while True:
            steps = 0
            # move right while target is bigger than current
            # <= to maintain insertion
            while True:
                rnode, width = node.get_right(level)
                if rnode == self.__tail:
                    break
                elif self.__key_provider(rnode.val) <= self.__key_provider(val):
                    steps += width
                    node = rnode
                else:
                    break

            # check if currently at base level
            if return_path:
                rightmosts.append((node, steps))
            if level != 0:
                level -= 1
            else:
                if return_path:
                    return rightmosts
                else:
                    return node

    def pprint(self):
        """
        pretty print for debugging

        :return:
        """
        base_nodes = list(self.__head.iter_level(level=0))
        base_nodes_str = [n.__str__() for n in base_nodes]
        print(','.join(base_nodes_str))
        for level in range(1, self.__head.num_levels):
            strings = []
            idx = 0
            for node, width in self.__head.iter_level(level):
                while node != base_nodes[idx][0]:                  # if node doesn't exist at this level
                    false_str = '-'*len(base_nodes_str[idx])    # append false string
                    strings.append(false_str)
                    idx += 1
                # corresponding found
                strings.append(str((node, width)))
                idx += 1
            print(','.join(strings))

    class __Node:
        def __init__(self, val):
            self.__val = val
            self._right = []   # node, width

        def __str__(self):
            return f"<Node:{self.__val}>"

        def __repr__(self):
            return self.__str__()

        @property
        def val(self):
            return self.__val

        @property
        def num_levels(self):
            return len(self._right)

        def get_right(self, level):
            if level < len(self._right):
                return self._right[level]
            return None

        def set_right(self, level, node, width):
            """
            accept replacement and appending

            :param level: level to set node at
            :param node: node to set
            :return:
            """
            if level == self.num_levels:
                self._right.append((node, width))
            elif level < self.num_levels:
                self._right[level] = (node, width)
            else:
                raise KeyError

        def iter_level(self, level):
            """
            iter nodes at level beginning from self

            :param level: iter level
            :return:
            """
            node_width = (self, 0)
            while True:
                yield node_width
                node_width = node_width[0].get_right(level)
                if node_width is None:
                    break

        def delete(self):
            """
            called by SkipList.remove(), releases members

            :return:
            """
            self.__val = None
            self._right = None

    class __HeadNode(__Node):
        def __init__(self):
            super().__init__(-inf)

        def pop_level(self):
            """
            remove level, only allowed for head node

            :return:
            """
            return self._right.pop()

    class __TailNode(__Node):
        def __init__(self):
            super().__init__(inf)

if __name__ == '__main__':
    sl = SkipList()
    sl.pprint()
    for i in range(5):
        sl.push(i)
    sl.pprint()
    sl.remove(0)
    print()
    sl.pprint()
    sl.remove(1)
    print()
    sl.pprint()
    sl.remove(2)
    print()
    sl.pprint()
    sl.remove(3)
    print()
    sl.pprint()
    sl.remove(4)
    print()
    sl.pprint()
    for i in range(5):
        sl.push(random.randint(0, 10))
    sl.pprint()
    # print(sl[-5])
    print('66666')
    print(sl.pop())
    print(sl.pop())
    print(sl.pop())
    print(sl.pop())
    sl.pprint()
    print(sl.pop())
    print(sl.pop())
    sl.pprint()
    # k = SkipList()
    # print(bool(k))
    # k.push(5)
    # print(bool(k))
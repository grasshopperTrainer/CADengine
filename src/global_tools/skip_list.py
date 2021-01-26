import random
from math import inf


class SkipList:
    def __init__(self):
        self.__head = self.__Node(-inf)
        self.__tail = self.__Node(inf)
        self.__head.set_right(level=0, node=self.__tail)
        self.__size = 0

    def __str__(self):
        return f"<SkipList: {self.__size}/{self.__head.num_levels}>"

    def put(self, val):
        """
        insert new value

        :param val:
        :return:
        """
        target_node = self.__Node(val)
        node_path = self.__search_path(val)
        for level, lnode in enumerate(reversed(node_path)):
            # stop growing in level if coil flip fails, but dont if in base level
            if level != 0 and not self.__flip_coin():
                break
            # grow in level
            self.__insert(lnode, target_node, level)
        # target node topped existing level if not broken.
        # add new level -> but why is this needed?
        else:
            self.__head.set_right(level=self.__head.num_levels, node=self.__tail)
        # mark size growth
        self.__size += 1

    def remove(self, val):
        raise NotImplementedError

    def remove_all(self, val):
        raise NotImplementedError

    def __insert(self, lnode, target, level):
        """
        linked list insertion

        :param lnode:
        :param target:
        :return:
        """
        rnode = lnode.get_right(level=level)
        target.set_right(level=level, node=rnode)
        lnode.set_right(level=level, node=target)

    def __flip_coin(self):
        """
        1/2 probability coin flip

        :return: bool
        """
        return bool(random.getrandbits(1))

    def __search_path(self, val):
        """
        search node path that leads to equal or less of given value

        :param val: list, rightmost nodes on each level
        :return:
        """
        level = self.__head.num_levels-1
        node = self.__head
        rightmosts = []
        while True:
            # move right while target is bigger than current
            # <=to maintain insertion order
            while node.get_right(level).val <= val:
                node = node.get_right(level)
            # check if currently at base level
            rightmosts.append(node)
            if level != 0:
                level -= 1
            else:
                return rightmosts

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
            for node in self.__head.iter_level(level):
                while node != base_nodes[idx]:                  # if node doesn't exist at this level
                    false_str = '-'*len(base_nodes_str[idx])    # append false string
                    strings.append(false_str)
                    idx += 1
                # corresponding found
                strings.append(base_nodes_str[idx])
                idx += 1
            print(','.join(strings))

    class __Node:
        def __init__(self, val):
            self.__val = val
            self.__right = []

        def __str__(self):
            return f"<Node:{self.__val}>"

        def __repr__(self):
            return self.__str__()

        @property
        def val(self):
            return self.__val

        @property
        def num_levels(self):
            return len(self.__right)

        def get_right(self, level):
            if level < len(self.__right):
                return self.__right[level]
            return None

        def set_right(self, level, node):
            """
            accept replacement and appending

            :param level: level to set node at
            :param node: node to set
            :return:
            """
            if level == self.num_levels:
                self.__right.append(node)
            elif level < self.num_levels:
                self.__right[level] = node
            else:
                raise KeyError

        def iter_level(self, level):
            """
            iter nodes at level beginning from self

            :param level: iter level
            :return:
            """
            node = self
            while True:
                yield node
                node = node.get_right(level)
                if node is None:
                    break


if __name__ == '__main__':
    sl = SkipList()
    for _ in range(5):
        i = random.randint(0, 50)
        sl.put(i)
    sl.pprint()
    print(sl)
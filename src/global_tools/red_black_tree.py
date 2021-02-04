from collections import deque
from global_tools.singleton import Singleton


class RedBlackTree:

    def __init__(self, comparator=None):
        """

        :param comparator: function that returns comparison between object(value being inserted) and
                            subject(value in list being compared).
                            ! First argument of the function has to be object and second should be subject.
                            ! Equal should return, terminate search, 0
                            ! if object less than subject, continue search left, return -1
                            ! if object greater than subject, continue search right, return +1
        """
        self.__root = None
        if not (comparator is None or callable(comparator)):
            raise TypeError
        self.__comparator = comparator
        self.__size = 0
        self.__itercount = 0

    def __contains__(self, val):
        """
        instance membership test
        No logical equality tested.
        :param val:
        :return:
        """
        try:
            self.__search_value(val)
        except ValueError as e:
            raise e
        except:
            raise Exception('unknown')

    def __str__(self):
        return f"<RBTree,{self.__size}>"

    def __len__(self):
        return self.__size

    def __iter__(self):
        """
        traverse inorder

        :return:
        """
        if not self.__size:
            return ()

        def traverse(node):
            if node.is_null:
                return
            else:
                yield from traverse(node.left)
                yield node.val
                yield from traverse(node.right)
        return traverse(self.__root)

    def __getitem__(self, item):
        for i, node in enumerate(self):
            if i == item:
                return node.val
        raise IndexError

    def __search_parent(self, val):
        """
        return parent of given value

        :param val:
        :return:
        """
        node = self.__root
        while True:
            comparison = self.__compare_value(obj=val, subj=node.val)
            # continue search
            if comparison == -1:
                if node.left.is_null:
                    return node
                node = node.left
            else:
                if node.right.is_null:
                    return node
                node = node.right

    def __search_value(self, val):
        """
        return node of given value
        :param val:
        :return:
        """
        node = self.__root
        while not node.is_null:
            comparison = self.__compare_value(obj=val, subj=node.val)
            if comparison == 0:
                return node
            # continue search
            if comparison == -1:
                node = node.left
            else:
                node = node.right
        raise ValueError('no value')

    def __compare_value(self, obj, subj):
        if self.__comparator is None:
            if obj == subj:
                return 0
            elif obj < subj:
                return -1
            else:
                return 1
        else:
            return self.__comparator(obj, subj)

    def __transplant(self, old, new):
        """
        imagine cutting an old branch and gluing a new one
        Offsprings of new branch is all brought with it
        while old branch turns unseen as it looses connection from the tree.

        :param old:
        :param new:
        :return:
        """

        # clean new's relationship
        if not new.is_root:
            if new.parent.left is new:
                new.parent.reset_left()
            else:
                new.parent.reset_right()
        new.reset_parent()
        # new relationship
        # transplanting new
        if old.is_root:
            new.parent = old.parent
            self.__root = new
        else:
            if old.is_left:
                old.parent.left, new.parent = new, old.parent
            else:
                old.parent.right, new.parent = new, old.parent
        # clean old's relationship
        old.reset_parent()

    def __delete_fix(self, x):
        if x.is_root:
            x.color_black()
            return

        if x.is_red:  # case 0
            x.color_black()
        else:
            s = x.sibling
            if s.is_red:  # case 1
                # coloring
                s.color_black()
                x.parent.color_red()
                # rotate
                if x.is_left:
                    self.__rotate_left(pivot=s)
                else:
                    self.__rotate_right(pivot=s)
                self.__delete_fix(x)
            else:
                if s.left.is_black and s.right.is_black:  # case 2
                    s.color_red()
                    x = x.parent
                    if x.is_red:
                        x.color_black()
                    else:
                        self.__delete_fix(x)
                elif x.is_left:
                    if s.left.is_red and s.right.is_black:  # case 3
                        s.left.color_black()
                        s.color_red()
                        self.__rotate_right(pivot=s.left)
                        self.__delete_fix(x)
                    else:  # case 4
                        s.color_red() if s.parent.is_red else s.color_black()
                        s.parent.color_black()
                        s.right.color_black()
                        self.__rotate_left(pivot=s)
                else:
                    if s.left.is_black and s.right.is_red:  # case 3
                        s.right.color_black()
                        s.color_red()
                        self.__rotate_left(pivot=s.right)
                        self.__delete_fix(x)
                    else:  # case 4
                        s.color_red() if s.parent.is_red else s.color_black()
                        s.parent.color_black()
                        s.left.color_black()
                        self.__rotate_right(pivot=s)

    def __rotate_left(self, pivot):
        old_parent = pivot.parent
        old_left = pivot.left
        self.__transplant(old=pivot.parent, new=pivot)
        self.__transplant(old=pivot.left, new=old_parent)
        pivot.left.right, old_left.parent = old_left, pivot.left

    def __rotate_right(self, pivot):
        old_parent = pivot.parent
        old_right = pivot.right
        self.__transplant(old=pivot.parent, new=pivot)
        self.__transplant(old=pivot.right, new=old_parent)
        pivot.right.left, old_right.parent = old_right, pivot.right

    def delete(self, v):
        d = self.__search_value(v)
        # removing last
        if d.is_root and d.is_leaf:
            d.delete()
            self.__root = None
            return
        if d.left.is_null:
            r = x = d.right
            self.__transplant(old=d, new=x)
        elif d.right.is_null:
            r = x = d.left
            self.__transplant(old=d, new=x)
        else:
            r = d.successor
            x = r.right
            self.__transplant(old=r, new=x)
            if not d.is_root:
                if d.is_left:
                    r.parent, r.parent.left = d.parent, r
                else:
                    r.parent, r.parent.right = d.parent, r
            r.left, r.right = d.left, d.right
            r.left.parent, r.right.parent = r, r
        # fix
        if d.is_red:  # deleted red
            if r.is_null or r.is_red:
                pass
            else:  # r.is_black
                r.color_red()
                self.__delete_fix(x)
        else:  # deleted black
            if r.is_null or r.is_black:
                self.__delete_fix(x)
            else:  # replaced is red
                r.color_black()
        # cleanup
        self.__size -= 1
        d.delete()
        if not self.__size:
            self.__root = None
            r.delete()
        elif r.is_root:
            self.__root = r

    def __restructure(self, parent, me):
        # store grand grand parent
        gparent = parent.parent

        # new parenting
        if parent.is_left and me.is_left:
            self.__rotate_right(parent)
            x = parent
        elif parent.is_right and me.is_right:
            self.__rotate_left(parent)
            x = parent
        elif parent.is_left:
            self.__rotate_left(pivot=me)
            self.__rotate_right(pivot=me)
            x = me
        else:
            self.__rotate_right(pivot=me)
            self.__rotate_left(pivot=me)
            x = me

        # recolor
        x.color_black()
        x.left.color_red()
        x.right.color_red()

    def __recolor(self, parent):
        # store grand grand parent
        ggparent = parent.parent.parent
        gparent = parent.parent
        uncle = parent.sibling
        # recolor
        uncle.color_black()
        parent.color_black()
        gparent.color_red()
        if gparent.is_root:
            gparent.color_black()
        else:
            parent, me = ggparent, gparent
            if parent.is_red and me.is_red:
                uncle = parent.sibling
                if uncle.is_red:
                    self.__recolor(parent)
                else:
                    self.__restructure(parent, me)

    def insert(self, val):
        # initiation
        if self.__root is None:
            root = self.__Node(val, parent=None)
            root.color_black()
            self.__root = root
        else:
            parent = self.__search_parent(val)
            new_node = self.__Node(val, parent)
            comparison = self.__compare_value(obj=val, subj=parent.val)
            # set position
            if comparison == -1:  # value less
                parent.left = new_node
            elif comparison in (0, 1):  # value bigger equal
                parent.right = new_node
            # check fix
            if parent.is_red:
                if parent.parent.has_black_child:
                    self.__restructure(parent, new_node)
                else:
                    self.__recolor(parent)
        self.__size += 1

    def uprint(self):
        """
        ugly print for debugging

        :return:
        """

        if not self.__root:
            return
        parents = [self.__root]
        while parents:
            new_ps = []
            string = []
            for p in parents:
                if p.is_null:
                    string.append('----')
                else:
                    string.append(p.__str__())
                    new_ps.append(p.left)
                    new_ps.append(p.right)
            print(string)
            parents = new_ps
        print()

    class __Node:

        class __NullNode:
            """
            Null indicator, single instance enough
            """

            def __init__(self, parent):
                self.parent = parent
                self.is_null = True
                self.is_red = False
                self.is_black = True

            def __str__(self):
                return f"<B NULL>"

            def __repr__(self):
                return self.__str__()

            def color_black(self):
                pass

            @property
            def is_left(self):
                return self.parent.left is self

            @property
            def is_right(self):
                return self.parent.right is self

            @property
            def is_root(self):
                return self.parent is None

            @property
            def sibling(self):
                if self.parent:
                    return self.parent.left if self.is_right else self.parent.right
                return None

            def delete(self):
                """
                release instance

                :return:
                """
                self.parent = None
                self.is_null = None
                self.is_red = None
                self.is_black = None

            def reset_parent(self):
                self.parent = None

        def __init__(self, val, parent=None):
            self.val = val
            self.__is_red = True
            self.parent = parent
            self.right = self.__NullNode(self)
            self.left = self.__NullNode(self)
            self.is_null = False

        def __str__(self):
            return f"<{'R' if self.__is_red else 'B'} {self.val}>"

        def __repr__(self):
            return self.__str__()

        @property
        def is_red(self):
            return self.__is_red

        @property
        def is_black(self):
            return not self.__is_red

        @property
        def is_left(self):
            return self.parent.left is self

        @property
        def is_right(self):
            return self.parent.right is self

        @property
        def is_leaf(self):
            return self.left.is_null and self.right.is_null

        @property
        def is_root(self):
            return self.parent is None

        @property
        def sibling(self):
            return self.parent.left if self.is_right else self.parent.right

        @property
        def has_black_child(self):
            """
            check if any of children is black

            :return:
            """
            return not (self.right.is_red and self.left.is_red)

        @property
        def successor(self):
            node = self.right
            while not node.left.is_null:
                node = node.left
            return node

        @property
        def rightmost(self):
            node = self
            while not node.right.is_null:
                node = node.right
            return node

        def color_red(self):
            self.__is_red = True

        def color_black(self):
            self.__is_red = False

        def reset_left(self):
            """
            remove left by setting NILL node

            :return:
            """
            self.left.reset_parent()
            self.left = self.__NullNode(self)

        def reset_right(self):
            """
            remove right by setting NILL node

            :return:
            """
            self.right.reset_parent()
            self.right = self.__NullNode(self)

        def reset_parent(self):
            self.parent = None

        def delete(self):
            """
            release resources

            :return:
            """
            self.val = None
            self.__is_red = None
            self.parent = None
            self.right = None
            self.left = None
            self.is_null = None


if __name__ == '__main__':
    rb = RedBlackTree()
    for i in range(20):
        rb.insert(i)
    print('removing')
    # for i in reversed(range(20)):
    #     print('index', i)
    #     rb.delete(i)
    #     rb.uprint()
    for i in rb:
        print(i)
    # rb.push(10)
    # rb.push(20)
    # rb.push(30)
    # rb.push(40)
    # rb.push(50)
    # rb.push(60)
    # rb.push(70)
    # print()
    # print('inserting 80')
    # rb.push(80)
    # rb.push(40)
    # rb.uprint()
    # print()
    # print('inserting 40')
    # rb.push(40)
    # rb.push(40)
    # rb.push(40)
    # rb.push(0)
    # rb.push(100)
    # rb.push(20)
    # # # print()
    # # # print('putting', 35)
    # rb.push(35)
    # rb.uprint()
    # print()
    # # # print()
    # print('putting', 40)
    # rb.push(40)
    # rb.push(40)
    # rb.push(21)
    # rb.push(22)
    # rb.push(23)
    # rb.push(24)
    # rb.uprint()
    # rb.delete(40)
    # rb.delete(40)
    # rb.delete(35)
    # rb.delete(10)
    # rb.delete(20)
    # # rb.uprint()
    # rb.delete(30)
    # rb.delete(70)
    # rb.delete(100)
    # rb.delete(40)
    # rb.delete(40)
    # rb.delete(0)
    # # rb.delete(100)
    # # rb.uprint()
    # rb.delete(40)
    # rb.delete(40)
    # rb.delete(40)
    # rb.delete(20)
    # rb.delete(80)
    # rb.delete(60)
    # print()
    # print('removing last')
    # print(len(rb))
    # rb.delete(50)
    # rb.uprint()
    # # print('end')
    # # rb.push(100)
    # # rb.uprint()
    # # rb.delete(50)
    # # rb.delete(60)

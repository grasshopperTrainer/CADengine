import weakref as wr


class SingletonClass:
    """
    Singleton class
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            ins = super().__new__(cls)
            cls._instance = ins
            return ins

        # not to load __init__ twice, simply erase it
        if '__init__' in cls._instance.__class__.__dict__:
            delattr(cls._instance.__class__, '__init__')
        return cls._instance


class NotRelatableError(TypeError):

    def __init__(self, inst):
        self.inst = wr.ref(inst)

    def __str__(self):
        return f"< {self.inst.__class__.__name__} not a subclass of <ParentChildren> >"


class ParentChildren:
    _PC_prefix = '_PC'

    def parent_set(self, parent_obj):
        """
        Set parent
        :param parent_obj:
        :return:
        """

        if not isinstance(parent_obj, ParentChildren):
            raise NotRelatableError(parent_obj)
        # set parent
        attr_n = f"{self._PC_prefix}_parent"
        setattr(self, attr_n, wr.ref(parent_obj))
        # push self to parent obj
        parent_obj.children_append(self)

    def parent_get(self):
        """
        Get parent
        :return:
        """

        attr_n = f"{self._PC_prefix}_parent"
        if hasattr(self, attr_n):
            return getattr(self, attr_n)()
        return None

    def children_append(self, *child_obj):
        """
        Append multiple children
        :param child_obj:
        :return:
        """

        # initing attribute
        # have both list, set for indexing and searching
        list_n = f"{self._PC_prefix}_children_list"
        set_n = f"{self._PC_prefix}_children_set"
        if not hasattr(self, list_n):
            setattr(self, list_n, [])
        if not hasattr(self, set_n):
            setattr(self, set_n, wr.WeakSet())

        # discard if already a child
        l, s = getattr(self, list_n), getattr(self, set_n)
        for c in child_obj:
            if isinstance(c, (list, tuple)):
                raise TypeError("function accepts variadic parameter")
            elif not isinstance(c, ParentChildren):
                raise NotRelatableError(ParentChildren)

            if c not in s:
                # bidirectional relating
                l.append(wr.ref(c))
                s.add(c)
                c.parent_set(self)

    def children_get(self, *idx):
        """
        Returns list of children
        :param idx: index of desired children
        :return: list(children of given index) if idx is many else a child
        """
        attr_n = f"{self._PC_prefix}_children_list"
        if hasattr(self, attr_n):
            children = []

            for i in idx:
                if isinstance(i, (list, tuple)):
                    raise TypeError("function accepts variadic parameter")
                elif not isinstance(i, int):
                    raise TypeError(f"index value should be given")
                children.append(getattr(self, attr_n)[idx]())

            if len(children) == 1:
                return children[0]
            return children
        else:
            return None

    def children_iter(self):
        """
        Returns generator of children
        :return:
        """
        attr_name = f"{self._PC_prefix}_children_list"
        if not hasattr(self, attr_name):
            return []

        for c in getattr(self, attr_name):
            if c() is not None:
                yield c()


if __name__ == '__main__':
    class A(SingletonClass):

        def __init__(self):
            print('initiation A')
        pass

    a = A()
    b = A()
    c = A()
    print(a, b, c)
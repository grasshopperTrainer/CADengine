from collections import deque
import heapq


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
        self.inst = inst

    def __str__(self):
        return f"-<{self.inst.__class__.__name__}> not a subclass of <FamilyMember>-"


class TimeParadoxError(AttributeError):

    def __init__(self, obj, relationship, subj):
        """
        Loop detected in parent-child relationship

        Trying to set parent as child or child as parent.
        Translate attribute as `{obj} is {relationship} of {subj}`
        :param obj:
        :param relationship:
        :param subj:
        """
        self._obj = obj
        self._subj = subj
        self._relationship = relationship

    def __str__(self):
        return f"-{self._obj.__str__()} is already a {self._relationship.upper()} of {self._subj.__str__()}-"


class MemberIterator:
    def __init__(self):
        raise NotImplementedError
    def __next__(self):
        raise NotImplementedError
    def __iter__(self):
        raise NotImplementedError
    def __len__(self):
        raise NotImplementedError


class ParentIterator(MemberIterator):

    def __init__(self, start_at):
        self._start_at = start_at
        self._members = self._start_at.fm_get_parents()
        self._iter_idx = 0

    def __next__(self):
        if self._iter_idx >= len(self._members):
            raise StopIteration
        m = self._members[self._iter_idx]
        self._iter_idx += 1
        return m

    def __iter__(self):
        self._iter_idx = 0
        return self

    def __len__(self):
        return len(self._start_at.fm_get_parents())


class ChildrenIterator(MemberIterator):

    def __init__(self, start_at):
        self._start_at = start_at
        self._members = self._start_at.fm_get_children()
        self._iter_idx = 0

    def __next__(self):
        if self._iter_idx >= len(self._members):
            raise StopIteration
        m = self._members[self._iter_idx]
        self._iter_idx += 1
        return m

    def __iter__(self):
        self._iter_idx = 0
        return self

    def __len__(self):
        return len(self._members)


class FamilyMember:
    """
    Inheritor. Adds family tree functionality to class.
    Not like 'tree', this supports polygamy structure - multiple parent.
    Mono, polygamy functionality is supported by differentiating `set` `append` in method naming convention.
    """
    _ATTR_PREFIX = '_fm'
    _PARENT = 'parent'
    _CHILD = 'child'

    ITER_PARENT = ParentIterator
    ITER_CHILDREN = ChildrenIterator

    def _getdefault_attribute(self, attr_name, def_val):
        """
        Assign's attribute if nonexistant and return attribute
        :param attr_name: name of attribute
        :param def_val: default value of attribute
        :return:
        """
        if not hasattr(self, attr_name):
            setattr(self, attr_name, def_val)
        return getattr(self, attr_name)

    @property
    def _children_list(self):
        list_n = f"{self._ATTR_PREFIX}_children_list"
        return self._getdefault_attribute(list_n, [])

    @property
    def _children_set(self):
        set_n = f"{self._ATTR_PREFIX}_children_set"
        return self._getdefault_attribute(set_n, set())

    @property
    def _parent_list(self):
        list_n = f"{self._ATTR_PREFIX}_parent_list"
        return self._getdefault_attribute(list_n, [])
        
    @property
    def _parent_set(self):
        set_n = f"{self._ATTR_PREFIX}_parent_set"
        return self._getdefault_attribute(set_n, set())

    def _typ_check(self, obj):
        if not isinstance(obj, FamilyMember):
            raise TypeError

    def _paradox_check(self, relationship, subj):
        """
        Check Timeparadox.

        Whether trying to set parent as child of child as parent.
        Think of loop.
        Translate attributes as statement `{self} is {desired_rel} of {subj}`
        :param self: object
        :param relationship:
        :param subj:
        :return:
        """
        if relationship == self._PARENT:
            for offs in subj.fm_iter_preorder(self.ITER_CHILDREN):
                if offs == self:
                    raise TimeParadoxError(subj, relationship, self)

        elif relationship == self._CHILD:
            for anc in subj.fm_iter_preorder(self.ITER_PARENT):
                if anc == self:
                    raise TimeParadoxError(subj, relationship, self)
        else:
            raise TypeError

    def fm_set_parent(self, parent_obj):
        """
        Set monopoly parent.
        
        All other parents will be removed.
        If willing to add parent refer to `fm_append_parent`
        :param parent_obj: object to set as parent of this
        :return:
        """
        self._typ_check(parent_obj)
        self._paradox_check(self._CHILD, parent_obj)

        for parent in self._parent_list:
            parent.fm_remove_child(self)
        self._parent_list.clear()
        self._parent_list.append(parent_obj)
        self._parent_set.clear()
        self._parent_set.add(parent_obj)
        # push self to parent obj
        parent_obj.fm_append_child(self)

    def fm_append_parent(self, parent_obj):
        """
        Append parent

        If willing to set monopoly relationship refer to `fm_set_parent`
        :param parent_obj: object to set as parent of this
        :return:
        """
        self._typ_check(parent_obj)
        self._paradox_check(self._CHILD, parent_obj)

        if parent_obj not in self._parent_set:
            self._parent_list.append(parent_obj)
            self._parent_set.add(parent_obj)
            # append self as parent's child
            parent_obj.fm_append_child(self)

    def fm_remove_parent(self, parent_obj):
        self._typ_check(parent_obj)
        if parent_obj in self._parent_set:
            self._parent_list.remove(parent_obj)
            self._parent_set.remove(parent_obj)

    def fm_set_child(self, child_obj):
        """
        Set monopoly relationship with single child.

        All other children relationship will be removed.
        If willing to add child, refer to `fm_append_children`
        :param child_obj: objects to set as child of this
        :return:
        """
        self._typ_check(child_obj)
        self._paradox_check(self._PARENT, child_obj)

        for child in self._children_list:
            child.fm_remove_parent(self)
        self._children_list.clear()
        self._children_list.append(child_obj)
        self._children_set.clear()
        self._children_set.add(child_obj)
        # push self to parent obj
        child_obj.fm_append_parent(self)

    def fm_append_child(self, child_obj):
        """
        Append child.

        if willing to set monopoly relationship(single child)
        refer to `fm_set_child`
        :param child_obj: objects to append as children of this
        :return:
        """
        self._typ_check(child_obj)
        self._paradox_check(self._PARENT, child_obj)
        # discard if already a child
        if child_obj not in self._children_set:
            self._children_list.append(child_obj)
            self._children_set.add(child_obj)
            child_obj.fm_append_parent(self)

    def fm_remove_child(self, child_obj):
        self._typ_check(child_obj)
        if child_obj in self._children_set:
            self._children_list.remove(child_obj)
            self._children_set.remove(child_obj)

    def fm_get_parents(self):
        """
        Get copied list of parents
        :return:
        """
        return self._parent_list.copy()

    def fm_get_roots(self, visited=set()):
        """
        Return roots of family tree

        For monopoly parent family tree, single value list will be returned.
        Else does simple BFS search and returns all roots - member that has no parent
        :param visited: do not assign, in-function variable to prevent duplication
        :return: [single_root] or [roots, ...]
        """
        roots = []
        if not self._parent_set:
            return [self]
        else:
            for p in self.fm_iter_parents():
                if p not in visited:
                    visited.add(p)
                    roots += p.fm_get_roots(visited=visited)
        return roots

    def fm_get_children(self):
        """
        Return coyied list of children
        :param idx: index of desired children
        :return: list(children of given index) if idx is many else a child
        """
        return self._children_list.copy()
    
    def fm_iter_children(self):
        """
        Return generator of all children
        :return:
        """
        for child in self._children_list:
            yield child

    def fm_iter_parents(self):
        """
        Return generator of all parents
        :return:
        """

    def fm_iter_close_siblings(self):
        """
        Return generator of members sharing parents of this
        :return: 
        """
        raise NotImplementedError

    def fm_iter_all_siblings(self):
        """
        Return generator of all members of same generation
        :return: 
        """
        raise NotImplementedError

    def _member_iterator_check(self, iterator):
        if not issubclass(iterator, MemberIterator):
            raise TypeError("feed one if member iterator enum such as ITER_PARENT")

    def fm_iter_preorder(self, member_iterator):
        self._member_iterator_check(member_iterator)
        heap = [(1, i, m) for i, m in enumerate(member_iterator(self))]
        in_count = len(heap)
        depth_record = {m:1 for m in member_iterator(self)}
        while heap:
            level, _, member = heapq.heappop(heap)
            if depth_record.get(self, 0) >= level + 1:
                continue
            for next_member in member_iterator(member):
                if depth_record.get(next_member, 0) < level + 1:
                    depth_record[next_member] = level + 1
                    heapq.heappush(heap, (level+1, in_count, next_member))
                    in_count += 1
        for member, _ in sorted(depth_record.items(), key=lambda x: x[1]):
            yield member


    # def fm_iter_member(self, order_iterator, member_iterator):

    def fm_iter_postorder(self, member_iterator, _visited=None):
        this_is_origin = False
        if _visited is None:
            _visited = set()
            this_is_origin = True
        self._member_iterator_check(member_iterator)
        for member in member_iterator(self):
            if member not in _visited:
                _visited.add(member)
                for i in member.fm_iter_postorder(member_iterator, _visited=_visited):
                    yield i

        if not this_is_origin:
            yield self





if __name__ == '__main__':
    class A(FamilyMember):
        def __init__(self, sign):
            self._sign = sign

        def __str__(self):
            return f"<obj {self._sign}>"

        def __repr__(self):
            return self.__str__()

    m = [A(i) for i in range(14)]
    # set ancestors of m[6]
    m[0].fm_append_child(m[2])
    m[0].fm_append_child(m[3])
    m[1].fm_append_child(m[3])
    m[4].fm_append_child(m[6])
    m[2].fm_append_child(m[5])
    m[3].fm_append_child(m[5])
    m[3].fm_append_child(m[6])
    m[5].fm_append_child(m[6])
    # set offsprings of m[6]
    m[6].fm_append_child(m[7])
    m[6].fm_append_child(m[8])
    m[6].fm_append_child(m[9])
    m[7].fm_append_child(m[11])
    m[7].fm_append_child(m[12])
    m[8].fm_append_child(m[10])
    m[9].fm_append_child(m[10])
    m[10].fm_append_child(m[12])
    m[10].fm_append_child(m[13])

    a = m[6].fm_iter_postorder(ParentIterator)
    print(id(a))
    for i in a:
        print(i)
    print('--------------')
    for i in m[6].fm_iter_preorder(ParentIterator):
        print(i)
    print('_____________')
    b = m[6].fm_iter_postorder(ChildrenIterator)
    print(id(b))
    for i in b:
        print(i)
    print('_____________')
    for i in m[6].fm_iter_preorder(ChildrenIterator):
        print(i)
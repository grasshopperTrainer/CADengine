import weakref
from collections import OrderedDict
from global_tools.ListSet import ListSet


class TypewiseTracker:
    def __init__(self):
        self.__registry = _TypewiseRegistry()
        self.__stack = _TypewiseStack()

    @property
    def registry(self):
        return self.__registry

    @property
    def stack(self):
        return self.__stack


class _TypewiseRegistry:
    """
    Registry grouping entities by type.

    ex)
    class Foo:
        def __init__(self):
            self.__registry = TypewiseTracker()
            # registry usage
            self.__registry.register(self)

        def __delete__(self):
            for e in self.__registry:
                e.delete()

    """
    def __init__(self, reg_type=dict):
        """
        :param reg_type: dict-like instance, ex) dict or dict subclass or one of weakref dict instance
        """
        dict_like = dict, weakref.WeakKeyDictionary, weakref.WeakValueDictionary
        if isinstance(reg_type, dict_like):
            raise TypeError('data type for registry and stack should be dict-like')
        self.__registries = reg_type()

    def __getitem__(self, entity_cls):
        return list(self.__registries.get(entity_cls, {}))

    def __initget_subregistry(self, entity_cls):
        """
        initiate or get record per entity class

        :param entity_cls:
        :return:
        """
        return self.__registries.setdefault(entity_cls, ListSet())

    def iter(self, entity_cls):
        """
        iter all entities of given class in registered order

        :param entity_cls:
        :return: generator
        """
        for i in self.__initget_subregistry(entity_cls):
            yield i

    def get(self, entity_cls, idx):
        """
        retrive registered entity by entity type and index

        :param entity_cls:
        :param idx:
        :return:
        """
        if entity_cls in self.__registries and idx < len(self.__registries[entity_cls]):
            return list(self.__registries[entity_cls])[idx]
        else:
            return None

    def register(self, entity):
        """
        register entity

        ! using `OrderedDict` as ordered set
        :param entity:
        :return:
        """
        self.__initget_subregistry(entity.__class__).append(entity)

    def deregister(self, entity):
        """
        release entity

        :param entity:
        :return:
        """
        self.__initget_subregistry(entity.__class__).remove(entity)

    def is_registered(self, entity):
        """
        check if given entity is registered
        :param entity:
        :return:
        """
        return entity in self.__initget_subregistry(entity.__class__)

    def is_empty(self, entity_cls):
        return not bool(self.__initget_subregistry(entity_cls))


class _TypewiseStack:
    """
    Stack to record and track current entity of multiple types.

    Stack here describes a temporal hierarchical order of entities.
    The typical purpose of it is to track entity currency within python's context manager pattern.
    ex)
    class Foo:
        def __init__(self):
            self.__tracker = TypewiseStack()

        def __enter__(self):
            self.__tracker.put(self)

        def __exit__(self, ...):
            self.__tracker.pop(self)
    """

    def __init__(self, stack_type=dict):
        """
        :param stack_type: dict-like instance, ex) dict or dict subclass or one of weakref dict instance
        """
        dict_like = dict, weakref.WeakKeyDictionary, weakref.WeakValueDictionary
        if isinstance(stack_type, dict_like):
            raise TypeError('data type for registry and stack should be dict-like')
        self.__stacks = stack_type()

    def __getitem__(self, entity_type):
        """
        get stack of given entity type

        :param entity_type:
        :return: stack
        """
        # FIXME: this causes an unauthorized intrusion into stack
        return self.__stacks[entity_type]

    def __initset_substack(self, entity_type):
        """
        initiate or set stack per entity type

        :param entity_type:
        :return:
        """
        return self.__stacks.setdefault(entity_type, [])

    # stack methods
    def push(self, entity):
        self.__initset_substack(entity.__class__).append(entity)

    def pop(self, entity_cls):
        if not isinstance(entity_cls, type):
            raise TypeError('entity type should be popped must be indicated')
        if self.is_empty(entity_cls):
            raise _EmptyStackError('cant pop from empty stack')
        return self.__stacks[entity_cls].pop()

    def get_current(self, entity_type):
        if self.is_empty(entity_type):
            raise _EmptyStackError('no current from empty stack')
        return self.__initset_substack(entity_type)[-1]

    def get_current_byname(self, entity_type_name):
        """
        get current entity

        :param entity_type_name:
        :return:
        """
        for key_cls in self.__stacks:
            if key_cls.name == entity_type_name:
                return self.get_current(key_cls)
        raise _EmptyStackError('no current from empty stack')

    def is_empty(self, entity_cls):
        return not bool(self.__stacks.get(entity_cls, False))

    @property
    def stacks(self):
        return self.__stacks


class _EmptyStackError(Exception):
    def __init__(self, msg=''):
        self.__msg = msg

    def __str__(self):
        return self.__msg if self.__msg else "stack is empty"


class _RegistryError(Exception):
    def __init__(self, msg=''):
        self.__msg = msg

    def __str__(self):
        return self.__msg if self.__msg else "bas registry"
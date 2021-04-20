import weakref
from global_tools.list_set import ListSet
import abc


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


class TypewiseStacker:
    def __init__(self, stack_type=dict):
        """
        stack container that holds stacks for each unique types

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
        if entity_type not in self.__stacks:
            if not isinstance(entity_type, type):
                raise TypeError
            new_stack = _SubStack()
            self.__stacks[entity_type] = new_stack
            self.__stacks[entity_type.__name__] = new_stack
        return self.__stacks[entity_type]

    # stack methods
    def push(self, entity):
        stack = self[entity.__class__]
        stack.push(entity)

    def set_base(self, entity):
        stack = self[entity.__class__]
        stack.set_base(entity)


class _NoneBase:
    def __str__(self):
        return f"<NoneBase>"


class _SubStack:
    def __init__(self):
        self.__stack = []
        self.__base = _NoneBase()

    def __str__(self):
        return f"<Stack: {self.__base}, {self.__stack}>"

    # stack methods
    def push(self, entity):
        self.__stack.append(entity)

    def pop(self):
        if self.__stack:
            entity = self.__stack.pop()
        elif self.has_base():
            entity = self.__base
        else:
            raise _EmptyStackError('cant pop from empty stack')

        return entity

    def peek(self):
        if self.__stack:
            return self.__stack[-1]
        elif self.has_base():
            return self.__base
        else:
            raise _EmptyStackError('cant pop from empty stack')

    def peek_if(self):
        try:
            return self.peek()
        except _EmptyStackError:
            return None
        except Exception as e:
            raise e

    def has_base(self):
        if isinstance(self.__base, _NoneBase):
            return False
        return True

    def is_empty(self):
        if not isinstance(self.__base, _NoneBase) or self.__stack:
            return False
        return True

    def set_base(self, entity):
        """
        set base entity

        Base entity is the one that is under the stack;
        inpopable, returned when stack is empty
        :return:
        """
        self.__base = entity


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
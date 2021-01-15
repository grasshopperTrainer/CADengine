from ckernel.render_context._renderer import Renderer
import ckernel.render_context.opengl_context.opengl_hooker as hooked_opengl
from .context_stack import OpenglContextStack


class OpenglContext(Renderer):
    def __init__(self, context):
        """

        __entities: !not fully supported! better context know of its entities so
        those could be removed when context itself is removed
        :param context:
        """
        self._cntxt_manager = context
        self.__entities = OGLEntityRegistry()

    def __enter__(self):
        """
        put context in stack then make it current

        :return:
        """
        if OpenglContextStack.get_current() == self:    # remove duplicated binding
            OpenglContextStack.put_current(self)
        else:
            OpenglContextStack.put_current(self)
            with self._cntxt_manager.glfw as glfw:
                glfw.make_context_current()

        return hooked_opengl

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        need to releas window bound by make_context_current

        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        OpenglContextStack.pop_current()
        # return binding
        with OpenglContextStack.get_current()._cntxt_manager.glfw as glfw:
            glfw.make_context_current()

    @property
    def is_none(self):
        return False

    @property
    def entities(self):
        return self.__entities

    @property
    def context(self):
        return self._cntxt_manager


class OGLEntityRegistry:
    """
    Control, track OpenGL Entity(Object) existence and binding
    """
    def __init__(self):
        # this holds strong reference of the Entity, in case of deletion,
        # this, at the end, has to release the Entity
        self.__registry = {}
        # this holds stack for each type of entities
        self.__stacks = {}

    def append(self, entity):
        """
        track entity

        :param entity:
        :return:
        """
        self.__registry.setdefault(entity.__class__, []).append(entity)

    def remove(self, entity):
        """
        release entity

        :param entity:
        :return:
        """
        self.__registry[entity.__class__].remove(entity)

    def push(self, entity):
        self.__stacks.setdefault(entity.__class__, [None]).append(entity)

    def pop(self, entity_class):
        if self.is_stack_empty(entity_class):
            raise Exception('bad context management')
        return self.__stacks[entity_class].pop()

    def get_current(self, entity_class):
        return self.__stacks.setdefault(entity_class, [None])[-1]

    def get_current_byname(self, entity_name):
        for key_cls in self.__stacks:
            if key_cls.name == entity_name:
                return self.get_current(key_cls)
        return None

    def is_stack_empty(self, entity_class):
        return len(self.__stacks.get(entity_class, [None])) == 1

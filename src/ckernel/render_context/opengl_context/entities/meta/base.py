import weakref
import abc
import threading

from ckernel.render_context.opengl_context.entities.ogl_entities import OGLEntity
from ckernel.render_context.opengl_context.context_stack import get_current_ogl, OpenglUnboundError
from global_tools.lazy import lazyProp


class OGLMetaEntity(metaclass=abc.ABCMeta):
    """
    ! descriptor compatible : read instruction inside __init__
    ! inherit must
    ! abstractmethod:
        `_create_entity`    : method should create an Entity and return

    This class hides concrete context-wise entity, abstracting entity as application dependent not context.
    To work so, it implements factory like functionalities for creating concrete entities in relationship with a
    given(currently bound) OpenGL context.

    ! 'OGLEntity' doesnt mean the class only has to provide OpenGL entity, ex) vao, vbo, ibo.
    It's more like a logical description. 'OGLEntity' describes any object dependent to OGL context.
    """

    @lazyProp
    def __context_entity(self):
        """
        lazy parameter assignment

        this removes obligatory super().__init__()
        whilst creating entity storage when needed
        :return:
        """
        return weakref.WeakKeyDictionary()

    @lazyProp
    def __lock(self):
        """
        to lock `get_concrete` process
        :return:
        """
        return threading.Lock()

    def get_concrete(self):
        """
        return correct entity for the context

        Lazy initiating.
        If context is not given, entity of current context will be returned.
        :return: entity for current context
        """
        with self.__lock:
            c = get_current_ogl()
            if c is None:
                raise OpenglUnboundError

            # serve meta context not context
            meta = c.manager.meta_context
            # return if exists already
            if c in self.__context_entity:
                return self.__context_entity[c]
            if meta in self.__context_entity:
                return self.__context_entity[meta]
            # if not, create new and store
            with c:
                entity = self._create_entity()
                if not isinstance(entity, OGLEntity):
                    raise Exception('creator method is not wrapped, check opengl_hooked')
                if entity.is_shared:
                    self.__context_entity[meta] = entity
                else:
                    self.__context_entity[c] = entity
            return entity

    @abc.abstractmethod
    def _create_entity(self):
        """
        ! internal only : called by self.__get_concrete_entity()

        create new entity for a current context

        Implemented method assuming context is already bound.
        :return: newly created entity
        """

    def bind(self):
        self.get_concrete().bind()

    def unbind(self):
        self.get_concrete().unbind()

    def enter(self):
        """
        explicit context manager caller
        :return:
        """
        get_current_ogl().entity_stacker[self.__class__].push(self)
        self.bind()
        return self

    def exit(self):
        """
        explicit context manager exit
        :return:
        """
        stacker = get_current_ogl().entity_stacker[self.__class__]
        stacker.pop()
        if stacker.is_empty():
            self.unbind()
        elif stacker.peek() != self:
            stacker.peek().bind()

    def __enter__(self):
        """
        connector method, access entity through context manager patter when binding is needed

        :return:
        """
        return self.enter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        connector method

        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        return self.exit()

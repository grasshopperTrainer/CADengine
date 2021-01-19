import weakref
import abc

from .ogl_entities import OGLEntity
from .context_stack import OGLContextStack, OpenglUnboundError
from .error import *


class OGLEntityFactory(metaclass=abc.ABCMeta):
    """
    ! descriptor compatible : read instruction inside __init__
    ! inherit must
    ! abstractmethod:
        `_create_entity`    : method should create an Entity and return

    Factory class for creating entities in relationship with a given OpenGL context.
    ! 'OGLEntity' doesnt mean that the Factory only has to provide OpenGL entity, ex) vao, vbo, ibo.
    Its more like a logical description. 'OGLEntity' describes any object dependent to OGL context.
    """
    def __init__(self, is_descriptor):
        """
        ! inheritor must call this method to initiate base members

        :param is_descriptor: bool, determines the functionality of the class. There can be four cases in combination of
                            'is_descriptor' value and whether instance of this class is a class, or instance member of
                            another class. 3 out of 4 cases has usage while 1 is a contradictory definition and is not
                            guaranteed to function.

                            Case1 `is_descriptor` == True and 'class member' == True:
                            entity of context at the calling moment will be created lazily, if nonexistent, and returned
                            through __get__.

                            Case2 'is_descriptor' == True and 'class member' == False:
                            Contradiction. Will through Error when `create_entity` is called.

                            Case3 `is_descriptor` == False and 'class member' == True:
                            Instance will function as a simple factory method. Use `get entity` to retrieve entity.
                            If willing to use single Entity as a class member, simply chain instantiation and
                            `create_entity` to assign Entity, not Factory.
                            ex) class Foo:
                                entity = EntityFactory().create_entity()    # `entity` member has an Entity not Factory

                            Case4 `is_descriptor` == False and `class member` == False:
                            Instance will function as a simple factory method. Use `get entity` to retrieve entity.
        """
        self.__is_descriptor = is_descriptor
        self.__context_entity = weakref.WeakKeyDictionary()

    def __get_unique_entity(self):
        """
        return correct entity for the context

        Lazy initiating.
        If context is not given, entity of current context will be returned.
        :return: entity for current context
        """
        context = OGLContextStack.get_current()
        if context.is_none:
            raise OpenglUnboundError
        # return if exists already
        if context in self.__context_entity:
            return self.__context_entity[context]
        # if not, create new and store
        with context:
            entity = self._create_entity()
            if not isinstance(entity, OGLEntity):
                raise Exception('creator method is not wrapped, check opengl_hooked')
            self.__context_entity[context] = entity
        return entity

    def __get__(self, instance, owner):
        """

        :param instance:
        :param owner:
        :return:
        """
        # is a factory if not a descriptor
        if not self.__is_descriptor:
            return self
        return self.__get_unique_entity()

    def __set__(self, instance, value):
        raise Exception('no setting allowed')

    @abc.abstractmethod
    def _create_entity(self):
        """
        ! internal only : called by self.__get_entity()

        create new entity for a current context

        Implemented method assuming context is already bound.
        :return: newly created entity
        """

    def get_entity(self):
        """
        creator for non descriptive instance else, explicit getter for unique entity

        ! This method seems to be redundant as Descriptor's method is not accessible through
        `__get__`. Yet in case of other Factory object accepting another Factory as a member,
        can detour `__get__` and make use of unique Entity.

        `ckernel.render_context.opengl_context.ogl_factories.OGLVrtxArryFactory`
        :return:
        """
        if self.__is_descriptor:
            return self.__get_unique_entity()
        else:
            return self._create_entity()
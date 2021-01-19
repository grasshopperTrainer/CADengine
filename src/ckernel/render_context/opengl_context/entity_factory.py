import weakref
import abc

from .ogl_entities import OGLEntity
from .context_stack import OGLContextStack, OpenglUnboundError


class OGLEntityFactory(metaclass=abc.ABCMeta):
    """
    ! descriptor compatible : read instruction inside __init__
    ! inherit must
    ! abstractmethod:
        `_create_entity`    : method should create an Entity and return

    Factory class for creating entities in relationship with a given OpenGL context.
    ! 'OGLEntity' doesnt mean that the Factory only has to provide OpenGL entity, ex) vao, vbo, ibo.
    Its more like a logical description. 'OGLEntity' describes any object dependent to OGL context.

    This class can be used as descriptor and not.

    as a descriptor:
    entity of context at the calling moment will be created lazily, if nonexistent, and returned
    through __get__.

    as a none descriptor:
    Instance will function as a simple factory class. Use `get_entity` to retrieve unique entity.
    """

    @property
    def __context_entity(self):
        """
        lazy parameter assignment

        this removes obligation of super().__init__()
        whilst creating entity storage when needed
        :return:
        """
        name = '__context_entity'
        if not hasattr(self, name):
            setattr(self, name, weakref.WeakKeyDictionary())
        return self.__getattribute__(name)

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
        return self.__get_unique_entity()
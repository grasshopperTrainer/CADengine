from mkernel.global_id_provider import GIDP
import weakref as wr

"""
! shpae is a renderable thing.
! not all geometry is natively shape.
! think of plane. Its a geometric data but is not !seen!.
! it should be rendered as a box or collection of lines
! `Ray` is also natively not a `Shape`. It may has to be rendered simply as a long `line`.
! distinction: 'native shape, nonnative shape'
"""


class _MetaShape(type):
    def __new__(cls, name, bases, dic):
        """
        metaclass for shape, add property for goid and model

        :param name:
        :param bases:
        :param dic:
        """
        if bases:
            if '__dataset_size__' not in dic:
                raise AttributeError(f"<{name}> must provide method '__dataset_size__'")

        my_type = super().__new__(cls, name, bases, dic)
        # add hidden property
        my_type.__goid = None
        my_type.goid = property(fget=cls.goid)

        my_type.__parent = None
        my_type.parent = property(fget=cls.parent)

        my_type.__children = set()
        my_type.children = property(fget=cls.children)
        my_type.add_child = cls.add_child
        my_type.remove_child = cls.remove_child

        # not yet allowed
        # need to develop when resetting parent is open th the user
        # or maybe tree editing has to go through modeler, thus real functions invisible
        # my_type.set_parent = cls.set_parent

        return my_type

    def __call__(cls, *args, **kwargs):
        """
        add implicit attributes

        :param args:
        :param kwargs:
        :return:
        """
        obj = cls.__new__(cls)
        # force attribute
        obj.__goid = GIDP().register_entity(obj)

        # hijack kwarg, parenting
        if '__parent' not in kwargs:
            raise AttributeError
        parent = kwargs.pop('__parent')
        if parent is not None:
            obj.__parent = wr.ref(parent)
            parent.add_child(obj)

        obj.__init__(*args, **kwargs)
        return obj

    @staticmethod
    def goid(self):
        return self.__goid

    @staticmethod
    def parent(self):
        if self.__parent:
            p = self.__parent()
            if p:
                return p
            else:
                self.__parent = None

    @staticmethod
    def set_parent(self, parent):
        if parent is not None:
            self.__parent = wr.ref(parent)

    @staticmethod
    def children(self):
        return iter(self.__children)

    @staticmethod
    def add_child(self, child):
        self.__children.add(child)

    @staticmethod
    def remove_child(self, child):
        self.__children.remove(child)


class Shape(metaclass=_MetaShape):
    """
    metaclass applicated inheritable
    """
    pass

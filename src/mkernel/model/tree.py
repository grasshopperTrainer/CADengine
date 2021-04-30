import weakref as wr


class ModelNode:
    """
    memeber of model tree
    includes Model and Shape
    """

    def __init__(self, parent):
        if parent is None:
            self.__parent = None
        else:
            self.__parent = wr.ref(parent)
        self.__children = set()

    @property
    def parent(self):
        if self.__parent is not None:
            return self.__parent()

    @property
    def children(self):
        return iter(self.__children)

    def add_child(self, child):
        self.__children.add(child)

    def remove_child(self, child):
        self.__children.remove(child)

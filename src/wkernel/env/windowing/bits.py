from my_patterns import FamilyMember
from wkernel.hooked import glfw


class _Bit(FamilyMember):
    pass


class DrawBit(_Bit):
    """
    has draw call?
    """

    def draw(self):
        """
        Placeholder for chained draw call
        :return:
        """
        if hasattr(self, 'setup') and callable(getattr(self, 'setup')):
            getattr(self, 'setup')()
            for cls in self.__class__.__mro__:
                if 'setup' in cls.__dict__:
                    delattr(cls, 'setup')
                    break

        # call draw method of children
        for c in self.fm_all_children():
            if isinstance(c, DrawBit):
                c.draw()

    def setup(self):
        """
        Instant functions called once
        :return:
        """
        print('setup', self)
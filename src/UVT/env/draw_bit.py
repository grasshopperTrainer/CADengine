from ..patterns import FamilyTree


class DrawBit(FamilyTree):

    def draw(self):
        """
        Placeholder for chained draw call
        :return:
        """
        # call draw method of children
        for c in self.ftree_iter_children():
            if isinstance(c, DrawBit):
                c.draw()
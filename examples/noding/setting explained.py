# assignment will call descriprot's `__set__`
# then Interface buffer's `set_provoke_value`
# then `_signal_downstream`
some_node.some_input = another_node.some_output

class _IntfDescriptor:
    ...
    def __set__(self, instance: NodeBody, value):
        # retrive stored interface buffer
        intf = instance.get_intf(self._name)
        intf.set_provoke_value(value)
    ...


class _InputBffr(_IntfBffr):
    ...
    def set_provoke_value(self, value):
        """
        Set interface value

        whilst building relationship and resetting calculated flag
        :param value:
        :return:
        """
        super().set_provoke_value(value)
        # by default relationship is monopoly so clear
        self.fm_clear_parent()
        # make relationship
        if isinstance(value, _IntfBffr):
            # set relationship between interface
            self.fm_append_member(parent=value, child=self)
            value = value._value
        self._value = value
        self._signal_downstream()

    def _signal_downstream(self, visited=None, debug=''):
        """
        Reset children's calculated sign
        :return:
        """
    if visited == None:
        visited = set()
    if self._is_calculated():
        self._reset_calculated()
        for child in self.fm_all_children():
            if child not in visited:
                visited.add(child)
                child.reset_downstream(visited, debug + ' ' * 4)
    ...
class _IntfDescriptor:
    ...
    def __get__(self, instance: NodeBody, owner):
        intf = instance.get_intf(self._name)
        intf._recalculate_upstream()
        return intf
    ...


class _NodeMember(FamilyMember):
    ...
    def _recalculate_upstream(self, _visited=None, debug=''):
        """
        recalculated upstream to get up to date result

        :return:
        """
        if _visited is None: # initiate recursion
            _visited = set()
        if self._is_calculated(): # base condition
            return True
        is_parent_recalculated = True # flag for checking permanent recalculation
        # recursivly calculate upstream before calculating current
        for member in self.fm_all_parents():
            if not isinstance(member, _NodeMember):
                continue
            if member not in _visited:
                _visited.add(member)
                is_parent_recalculated &= member._recalculate_upstream(_visited, debug+' '*4)
        self._set_calculated()
        self._run_calculation()

        # if this node is set to permanently recalculate
        # or one of parent is set so, pass this signal downstream
        if self._calculate_permanent or not is_parent_recalculated:
            self._reset_calculated()
        return self._is_calculated()
    ...


class NodeBody(_NodeMember):
    ...
    def _run_calculation(self):
        """
        Execute concrete function and push value downstream
        :return:
        """
        # collect input
        input_vs = OrderedDict()
        for intf in self.input_intfs:
            if intf.sibling_intf_allowed:
                input_vs.setdefault(intf.family_name, []).append(intf.get_calculated_value())
            else:
                input_vs[intf] = intf.get_calculated_value()

        # run actual function defined by user
        try:
            results = self.calculate(*input_vs.values())
        except Exception as e:
            # set all outputs NULL
            results = [NullValue(f"calculation fail of {self}")] * len(self.output_intfs)
            # record and print error status
            self._calculation_status = e
            self.print_status()
        else:
            # wrap singular result and match length
            results = [results] if not isinstance(results, (list, tuple)) else list(results)
            results += [NullValue("calculation didn't return enough values")] * (len(self.output_intfs) - len(results))
            self._calculation_status = ''
        finally:
            # push calculation result down to outputs
            for result, intf in zip(results, self.output_intfs):
                intf.set_provoke_value(result)
    ...


class _InputBffr(_IntfBffr):
    ...
    def _run_calculation(self):
        """
        Nothing to do
        :return:
        """
        pass
    ...


class _OutputBffr(_IntfBffr):
    ...
    def _run_calculation(self):
        """
        Just push value downstream
        :return:
        """
        for child in self.fm_all_children():
            if isinstance(child, _IntfBffr):
                child._value = self._value
    ...
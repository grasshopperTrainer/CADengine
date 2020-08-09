from ._data import *
from ...data_types.primitive import *


class ConSingleNamedData(DataNode):
    """
    Build name data

    :param attr_name: name of data
    :param value: iterable values
    :param dtype: data type
    :param vattro: vertex attribute object
    """
    in0_name = Input(None)
    in1_data = Input(None)
    in2_dtype = Input(None)
    out0_ndata = Output(None)

    def __init__(self, attr_name, data, dtype):
        super().__init__()
        self.in0_name = attr_name
        self.in1_data = data
        self.in2_dtype = dtype

    def calculate(self, name, data, dtype):
        # convert 1D array into list
        if isinstance(data, np.ndarray) and len(data.shape) == 1:
            data = data.tolist()

        if isinstance(data, (tuple, list)):
            if not isinstance(data[0], (tuple, list)):
                data = tuple([data])
            dtype = np.dtype([(name, dtype, len(data[0]))])
            arr = np.zeros(len(data), dtype=dtype)
            arr[name][:] = data

        elif isinstance(data, np.ndarray):
            data = data.astype(dtype)
            # and when array is multi dimensional, store it as an array
            dtype = np.dtype([(name, np.ndarray)])
            arr = np.zeros(1, dtype=dtype)
            arr[0] = (data, )
        else:
            raise NotImplementedError(name, data, dtype)
        return NamedData(arr)


class ConCompoundNamedData(DataNode):
    pass


class JoinNamedData(DataNode):

    in0_ndata = Input(has_siblings=True)
    out0_ndata = Output()

    def calculate(self, ndata):
        arrays = [nd._data for nd in ndata]
        newdtype = sum((a.dtype.descr for a in arrays), [])
        joined_arr = np.empty(len(arrays[0]), dtype = newdtype)

        for a in arrays:
            for name in a.dtype.names:
                joined_arr[name] = a[name]
        return NamedData(joined_arr)

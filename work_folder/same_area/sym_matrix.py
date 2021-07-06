import numpy


class SymNDArray(numpy.ndarray):
    """
    NumPy array subclass for symmetric matrices.

    A SymNDArray arr is such that doing arr[i,j] = value
    automatically does arr[j,i] = value, so that array
    updates remain symmetrical.
    """

    def __setitem__(self, index, value):
        super(SymNDArray, self).__setitem__(index, value)
        super(SymNDArray, self).__setitem__((index[1], index[0]), value)


def symmetrize(a):
    """
    Return a symmetrized version of NumPy array a.

    Values 0 are replaced by the array value at the symmetric
    position (with respect to the diagonal), i.e. if a_ij = 0,
    then the returned array a' is such that a'_ij = a_ji.

    Diagonal values are left untouched.

    a -- square NumPy array, such that a_ij = 0 or a_ji = 0,
    for i != j.
    """
    return a + a.T - numpy.diag(a.diagonal())


def symarray(input_array):
    """
    Return a symmetrized version of the array-like input_array.

    The returned array has class SymNDArray. Further assignments to the array
    are thus automatically symmetrized.
    """
    return symmetrize(numpy.asarray(input_array)).view(SymNDArray)

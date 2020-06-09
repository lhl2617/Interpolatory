import numpy as np
from numba import njit

@njit
def _pad_simple(array, pad_width, fill_value=None):
    # Allocate grown array
    new_shape = tuple(
        left + size + right
        for size, (left, right) in zip(array.shape, pad_width)
    )
    order = 'F' if array.flags.fnc else 'C'  # Fortran and not also C-order
    padded = np.empty(new_shape, dtype=array.dtype, order=order)

    if fill_value is not None:
        padded.fill(fill_value)

    # Copy old array into correct space
    original_area_slice = tuple(
        slice(left, left + size)
        for size, (left, right) in zip(array.shape, pad_width)
    )
    padded[original_area_slice] = array

    return padded, original_area_slice

def _slice_at_axis(sl, axis):
    return (slice(None),) * axis + (sl,) + (...,)

def _view_roi(array, original_area_slice, axis):
    axis += 1
    sl = (slice(None),) * axis + original_area_slice[axis:]
    return array[sl]

def _as_pairs(x, ndim, as_index=False):
    if x is None:
        # Pass through None as a special case, otherwise np.round(x) fails
        # with an AttributeError
        return ((None, None),) * ndim

    x = np.array(x)
    if as_index:
        x = np.round(x).astype(np.intp, copy=False)

    if x.ndim < 3:
        # Optimization: Possibly use faster paths for cases where `x` has
        # only 1 or 2 elements. `np.broadcast_to` could handle these as well
        # but is currently slower

        if x.size == 1:
            # x was supplied as a single value
            x = x.ravel()  # Ensure x[0] works for x.ndim == 0, 1, 2
            if as_index and x < 0:
                raise ValueError("index can't contain negative values")
            return ((x[0], x[0]),) * ndim

        if x.size == 2 and x.shape != (2, 1):
            # x was supplied with a single value for each side
            # but except case when each dimension has a single value
            # which should be broadcasted to a pair,
            # e.g. [[1], [2]] -> [[1, 1], [2, 2]] not [[1, 2], [1, 2]]
            x = x.ravel()  # Ensure x[0], x[1] works
            if as_index and (x[0] < 0 or x[1] < 0):
                raise ValueError("index can't contain negative values")
            return ((x[0], x[1]),) * ndim

    if as_index and x.min() < 0:
        raise ValueError("index can't contain negative values")

    # Converting the array with `tolist` seems to improve performance
    # when iterating and indexing the result (see usage in `pad`)
    return np.broadcast_to(x, (ndim, 2)).tolist()

def _set_pad_area(padded, axis, width_pair, value_pair):
    """
    Set empty-padded area in given dimension.

    Parameters
    ----------
    padded : ndarray
        Array with the pad area which is modified inplace.
    axis : int
        Dimension with the pad area to set.
    width_pair : (int, int)
        Pair of widths that mark the pad area on both sides in the given
        dimension.
    value_pair : tuple of scalars or ndarrays
        Values inserted into the pad area on each side. It must match or be
        broadcastable to the shape of `arr`.
    """
    left_slice = _slice_at_axis(slice(None, width_pair[0]), axis)
    padded[left_slice] = value_pair[0]

    right_slice = _slice_at_axis(
        slice(padded.shape[axis] - width_pair[1], None), axis)
    padded[right_slice] = value_pair[1]

def pad(array, pad_width):
    array = np.asarray(array)
    pad_width = np.asarray(pad_width)

    # Broadcast to shape (array.ndim, 2)
    pad_width = _as_pairs(pad_width, array.ndim, as_index=True)

    # Create array with final shape and original values
    # (padded area is undefined)
    padded, original_area_slice = _pad_simple(array, pad_width)
    # And prepare iteration over all dimensions
    # (zipping may be more readable than using enumerate)
    axes = range(padded.ndim)

    values = _as_pairs(0, padded.ndim)
    for axis, width_pair, value_pair in zip(axes, pad_width, values):
        roi = _view_roi(padded, original_area_slice, axis)
        _set_pad_area(roi, axis, width_pair, value_pair)

    return padded


def bench(im, block_size):
    return np.pad(im, ((0, block_size), (0, block_size), (0,0)))

def bench2(im, block_size):
    return pad(im, ((0, block_size), (0, block_size), (0,0)))
    
a = np.ones((5,4, 3))

b = bench(a, 7)
c = bench2(a, 7)
print(b == c)
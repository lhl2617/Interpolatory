import numpy as np
from numba import njit, int32, float32, types

@njit(types.UniTuple(int32, 2)(float32[:,:]))
def helper(block_flat):
    total_row = 0.
    total_col = 0.
    total_weight = 0.
    weightings = np.asarray([1, 2, 1, 2, 6, 2, 1, 2, 1], dtype=np.float32)
    
    for i in range(block_flat.shape[0]):
        total_row += block_flat[i, 0] * weightings[i]
        total_col += block_flat[i, 1] * weightings[i]
        total_weight += weightings[i]
    return (total_row // total_weight, total_col // total_weight)
    
def weighted_mean_filter(block):
    block_flat = np.reshape(block, (-1, block.shape[-1]))
    return helper(block_flat)
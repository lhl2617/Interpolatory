import numpy as np
from numba import njit, float32
@njit
def helper(block_flat):
    sorted_idx_row = np.argsort(block_flat[:,0])
    sorted_idx_col = np.argsort(block_flat[:,1])
    median_idx_row = sorted_idx_row[sorted_idx_row.shape[0]//2]
    median_idx_col = sorted_idx_col[sorted_idx_col.shape[0]//2]
    row = block_flat[median_idx_row, 0]
    col = block_flat[median_idx_col, 1]
    return (row, col)

def median_filter(block):
    block_flat = block.reshape(-1, block.shape[-1])
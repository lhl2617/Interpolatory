import numpy as np

def weighted_mean_filter(block):
    weightings = [1, 2, 1, 2, 6, 2, 1, 2, 1]        # this will fuck up around borders (but thats one row of blocks so maybe its not that bad?) - only for 3x3
    block_flat = block.reshape(-1, block.shape[-1])
    total_row = 0
    total_col = 0
    total_weight = 0
    for i in range(block_flat.shape[0]):
        total_row += block_flat[i, 0] * weightings[i]
        total_col += block_flat[i, 1] * weightings[i]
        total_weight += weightings[i]
    return (int(total_row / total_weight), int(total_col / total_weight))

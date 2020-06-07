import numpy as np
def mean_filter(block):
    mean = np.mean(block, axis=(0,1))
    return (mean[0], mean[1])
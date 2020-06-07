from numba import jit, int32, float32, boolean, cu
import numpy as np
import cProfile
import math

# x = np.arange(100).reshape(10, 10)

# # @jit(nopython=True) # Set "nopython" mode for best performance, equivalent to @njit
# def go_fast(a): # Function is compiled to machine code when called the first time
#     trace = 0.0
#     for i in range(a.shape[0]):   # Numba likes loops
#         trace += np.tanh(a[i, i]) # Numba likes NumPy functions
#     return a + trace              # Numba likes NumPy broadcasting

# cProfile.run('print(go_fast(x))')

@jit(float32(int32), nopython=True)
def log2(n):
    return (math.log10(n) / math.log10(2))

@jit(boolean(int32), nopython=True)
def is_power_of_two(n):
    return (math.ceil(log2(n))) == math.floor(log2(n))

# @jit(float32(), nopython=True)
def go_fast():
    sum = 0.
    for i in range(2, 10000000):
        sum += log2(i)
        is_power_of_two(i)
    return sum

cProfile.run('print(go_fast())')
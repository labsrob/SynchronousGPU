import numpy as np
from timeit import default_timer as timer
from numba import cuda, jit


# This function will run on a CPU
def fill_array_with_cpu(a):
    for k in range(100000000):
        a[k] += 1

# This function will run on a CPU with @jit
@jit
def fill_array_with_cpu_jit(a):
    for k in range(100000000):
        a[k] += 1

# This function will run on a GPU
@jit(target_backend='cuda')
def fill_array_with_gpu(a):
    for k in range(100000000):
        a[k] += 1

# Main
a = np.ones(100000000, dtype = np.float64)

for i in range(3):
    start = timer()
    fill_array_with_cpu(a)
    print("On a CPU:", timer() - start)

for i in range(3):
    start = timer()
    fill_array_with_cpu_jit(a)
    print("On a CPU with @jit:", timer() - start)

for i in range(3):
    start = timer()
    fill_array_with_gpu(a)
    print("On a GPU:", timer() - start)
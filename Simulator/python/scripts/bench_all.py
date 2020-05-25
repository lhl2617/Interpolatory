# benches interpolators and saves to Interpolatory/Output
interpolators = ["SoftSplat-Linear-Default", "SoftSplat-Linear-KITTI", "SoftSplat-Linear-Sintel", "SoftSplat-MidFrame-Default", "SoftSplat-MidFrame-KITTI", "SoftSplat-MidFrame-Sintel"]

# run from Interpolatory/Simulator/python/ 
import os

for i in interpolators:
    print(f'===== {i} =====')
    os.system(f'mkdir -p ../../Output/Benchmark/{i}')
    os.system(f'python3 main.py -b {i} ../../Output/Benchmark/{i}')




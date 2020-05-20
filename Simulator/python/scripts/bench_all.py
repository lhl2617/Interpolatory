# benches interpolators and saves to Interpolatory/Output
interpolators = ['Linear', 'Oversample', 'Nearest', 'SepConvL1-CUDA', 'SepConvLf-CUDA', 'RRIN-CUDA']

# run from Interpolatory/Simulator/python/ 
import os

for i in interpolators:
    print(f'===== {i} =====')
    os.system(f'mkdir -p ../../Output/{i}')
    os.system(f'python3 main.py -b {i} ../../Output/{i}')




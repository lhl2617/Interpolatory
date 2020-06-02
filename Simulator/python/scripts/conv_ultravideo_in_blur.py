# to convert all for one interpolator

# run from Interpolatory/Simulator/python/ 

interpolator = 'RRIN-Linear-CUDA'

import os
import sys
import glob 

sep = os.path.sep

args = sys.argv[1:]

src_dst_frame_rates = [(30,60)]
ratios = [0.5]

root_path = '../../Datasets/ultravideo/blur'
for ratio in ratios:
    if ratio != 1:
        root_path = f'../../Datasets/ultravideo/blur/downsampled/{ratio}'
    for (src_frame_rate, dst_frame_rate) in src_dst_frame_rates:
        rawVids = glob.glob(f'{root_path}{sep}{src_frame_rate}fps{sep}*')
        for rawVidPath in rawVids:
            fileName = rawVidPath.split(sep)[-1]

            target_dir = f'../../Output/ultravideo/blur/ratio{ratio}/{src_frame_rate}-{dst_frame_rate}/{interpolator}'

            os.system(f'mkdir -p {target_dir}')

            target_file_path = f'{target_dir}/{fileName}'

            cmd = (f'python3 main.py -i {rawVidPath} -m {interpolator} -f {dst_frame_rate} -o {target_file_path}')
            print(cmd)
            os.system(cmd)

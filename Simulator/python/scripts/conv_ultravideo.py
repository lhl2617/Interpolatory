# converts ultra-video
# args: <src-frame-rate> <dst-frame-rate> [<ratio>]
# ratio is for the downsampled ones (0.5, 0.25)

# run from Interpolatory/Simulator/python/ 

interpolators = ['Nearest', 'Oversample', 'Linear', 'SepConvL1-CUDA', 'SepConvLf-CUDA', 'RRIN-MidFrame-CUDA', 'RRIN-Linear-CUDA']

# interpolators = ['SepConvL1-CUDA', 'SepConvLf-CUDA']

import os
import sys
import glob

sep = os.path.sep

args = sys.argv[1:]

src_frame_rate = args[0]
dst_frame_rate = args[1]
ratio = 1

root_path = '../../Datasets/ultravideo'

if len(args) > 2:
    ratio = args[2]
    root_path = f'../../Datasets/ultravideo/downsampled/{ratio}'

rawVids = glob.glob(f'{root_path}{sep}{src_frame_rate}fps{sep}*')

for interpolator in interpolators:
    for rawVidPath in rawVids:
        fileName = rawVidPath.split(sep)[-1]

        target_dir = f'../../Output/ultravideo/ratio{ratio}/{src_frame_rate}-{dst_frame_rate}/{interpolator}'

        os.system(f'mkdir -p {target_dir}')

        target_file_path = f'{target_dir}/{fileName}'

        cmd = (f'python3 main.py -i {rawVidPath} -m {interpolator} -f {dst_frame_rate} -o {target_file_path}')
        print(cmd)
        os.system(cmd)




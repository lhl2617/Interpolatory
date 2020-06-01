
mes = ['esa', 'tss', 'tdls', 'ntss', 'fss', 'ds', 'hexbs', 'epzs', 'umh'] # default  epzs
import os
import sys
import time
import glob 

src_vid_path = '../../Datasets/ultravideo/downsampled/0.5/30fps/Beauty.mp4'

for me in mes:
    minterpolate_string = f'\'mi_mode=mci:fps=60:me={me}\''

    out_vid_dir = '../../Output/ffmpeg_test_me'

    os.system(f'mkdir -p {out_vid_dir}')

    out_vid_path = f'{out_vid_dir}/{me}.mkv'

    start = int(round(time.time() * 1000))

    run_cmd = f'ffmpeg -i {src_vid_path} -filter:v \"minterpolate={minterpolate_string}\" {out_vid_path}'
    
    os.system(run_cmd)

    end = int(round(time.time() * 1000))

    print(f'{me}: took {float(end-start)/1000} seconds')
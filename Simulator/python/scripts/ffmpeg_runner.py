mc_modes = ['obmc', 'aobmc']
me_modes = ['bilat', 'bidir']
mes = ['esa', 'tss', 'tdls', 'ntss', 'fss', 'ds', 'hexbs', 'epzs', 'umh'] # default  epzs
# mb_sizes = [16]
# search_param = [32]
vsbmcs = [0, 1]

import os
import sys
import glob 

# run all the middlebury-1fps, then extract frame no. 2


paths = sorted(glob.glob(f'../../Datasets/middlebury-1fps/*/out.avi'))

for path in paths:
    middlebury_category = path.split('/')[-2]
    for mc_mode in mc_modes:
        for me_mode in me_modes:
            for me in mes:
                for vsbmc in vsbmcs:
                    minterpolate_string = f'\'mi_mode=mci:fps=2:mc_mode={mc_mode}:me_mode={me_mode}:me={me}:vsbmc={vsbmc}\''

                    id_string = f'{mc_mode}-{me_mode}-{me}-{vsbmc}'
                    
                    output_dir_base = f'../../Output/ffmpeg_test/{id_string}'

                    os.system(f'mkdir -p {output_dir_base}')

                    out_file_name = f'{output_dir_base}/{middlebury_category}_vid.avi'

                    run_cmd = f'ffmpeg -i {path} -filter:v \"minterpolate={minterpolate_string}\" {out_file_name}'
                    print(run_cmd)
                    os.system(run_cmd)

                    # extract the images
                    print('============================')
                    out_png_name = f'{output_dir_base}/{middlebury_category}.png'      
                    run_cmd = f'ffmpeg -i {out_file_name} -vf \"select=eq(n\\,1)\" -vframes 1 {out_png_name}'
                    print(run_cmd)
                    os.system(run_cmd)



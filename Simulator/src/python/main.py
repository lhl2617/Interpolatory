import sys
import json

from util import eprint
from Interpolator import InterpolatorDictionary


mode_flag = None

if (len(sys.argv) > 1):
    args = sys.argv[1:]
    mode_flag = args[0]

interpolators = list(InterpolatorDictionary.keys())
version = '0.0.1'

if mode_flag == '-h':
    print('======')
    print('Manual')
    print('======')

    print('')
    print('- python3 main.py -h')
    print('Get this help.')

    print('')
    print('- python3 main.py -if')
    print('Get supported interpolation-modes')
    
    print('')
    print('- python3 main.py -m <video-path>')
    print('Load a video and print metadata to stdout. If not supported, will return non-zero value')
    
    print('')
    print('- python3 main.py -i <input-video-path> -m <interpolation-mode> -f <output-frame-rate> -o <output-file-path>')
    print('Get in an input video source from <input-video-path> and, using <interpolation-mode> mode, interpolate to <output-frame-rate> fps and save to <output-file-path>')
    
    print('')
    print('- python3 main.py -b <interpolation-mode>')
    print('Run Middlebury benchmark to get results based on an <interpolation-mode>')
    
    print('')
    print('- python3 main.py -t <interpolation-mode> -f <frame1> <frame2> -o <output-file-path> [<ground-truth-path>]')
    print('Using <interpolation mode, get the interpolated midpoint frame between <frame1> and <frame2>, saving the output to <output-file-path>')
    print('If [<ground-truth-path>] provided, metrics (PSNR & SSIM) are returned')
    
    print('')
    print('- python3 main.py -ver')
    print('Get version')


elif mode_flag == '-if':
    print(json.dumps(interpolators))

elif mode_flag == '-m' and len(args) == 2:
    import imageio
    from io import BytesIO
    video_path = args[1]
    video_file = open(video_path, 'rb')
    content = video_file.read()
    video = imageio.get_reader(BytesIO(content), 'ffmpeg', loop=True)
    print(json.dumps(video.get_meta_data()))

    # print('')
    # print('- python3 main.py -i <input-video-path> -m <interpolation-mode> -f <output-frame-rate> -o <output-file-path>')
    # print('Get in an input video source from <input-video-path> and, using <interpolation-mode> mode, interpolate to <output-frame-rate> fps and save to <output-file-path>')
elif mode_flag == '-i' and len(args) == 8 and '-m' == args[2] and '-f' == args[4] and '-o' == args[6]:
    import math
    input_video_path = args[1]
    interpolation_mode = args[3]
    target_fps = int(args[5])
    output_video_path = args[7]

    interpolator_obj = InterpolatorDictionary[interpolation_mode]
    interpolator = interpolator_obj(target_fps, input_video_path, output_video_path, math.inf)
    interpolator.interpolate_video()

    # print(f'{input_video_path} - {interpolation_mode} - {target_fps} - {output_file_path}')
    # import time
    # for i in range (101):
    #     time.sleep(0.1)
    #     pct = str(i).rjust(3, ' ')
    #     print(f'PROGRESS::{pct}%::Frame whatever', flush=True)





    # print('')
    # print('- python3 main.py -b <interpolation-mode>')
    # print('Run Middlebury benchmark to get results based on an <interpolation-mode>')
elif mode_flag == '-b' and len(args) == 2:
    interpolation_mode = args[1]

    print(f'{interpolation_mode}')

    # print('- python3 main.py -t <interpolation-mode> -f <frame1> <frame2> -o <output-file-path> [<ground-truth-path>]')
    # print('Using <interpolation mode, get the interpolated midpoint frame between <frame1> and <frame2>, saving the output to <output-file-path>')
    # print('If [<ground-truth-path>] provided, metrics (PSNR & SSIM) are returned')
elif mode_flag == '-t' and len(args) >= 7 and '-f' == args[2] and '-o' == args[5] :
    interpolation_mode = args[1]
    frame_1_path = args[3]
    frame_2_path = args[4]
    output_file_path = args[6]
    ground_truth_path = None
    
    if (len(args) > 7):
        ground_truth_path = args[7]        
    print(f'{interpolation_mode} - {frame_1_path} - {frame_2_path} - {output_file_path} - {ground_truth_path}')

elif mode_flag == '-ver':
    print(json.dumps(version))

else:
    print(f'Unknown command. Run `python3 main.py -h` for a usage guide')

exit(0)






import sys
import imageio
from io import BytesIO
import json

args = sys.argv[1:]

mode_flag = args[0]

if mode_flag == '-h':
    print('======')
    print('Manual')
    print('======')
    print('')
    print('- python3 main.py -h')
    print('Get this help.')
    
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
    print('- python3 main.py -t <interpolation-mode> -f <frame1> <frame2> -o <output-file-path>')
    print('Using <interpolation mode, get the interpolated midpoint frame between <frame1> and <frame2>, saving the output to <output-file-path>')

    print('')
    print('TODO:- interpolation-mode listing')

elif mode_flag == '-m':
    video_path = args[1]
    video_file = open(video_path, 'rb')
    content = video_file.read()
    video = imageio.get_reader(BytesIO(content), 'ffmpeg', loop=True)
    print(json.dumps(video.get_meta_data()))

else:
    print(f'Unknown mode-flag `{mode_flag}`, run `python3 main.py -h` for a usage guide')

exit(0)






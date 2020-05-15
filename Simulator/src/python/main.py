import sys
import json

args = sys.argv[1:]

mode_flag = args[0]

interpolators = ['nearest', 'oversample', 'linear']
dependencies = ['imageio', 'imageio-ffmpeg', 'scikit-image', 'numpy', 'testdoesnotexist']
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
    print('- python3 main.py -t <interpolation-mode> -f <frame1> <frame2> -o <output-file-path>')
    print('Using <interpolation mode, get the interpolated midpoint frame between <frame1> and <frame2>, saving the output to <output-file-path>')
    
    print('')
    print('- python3 main.py -deps')
    print('Get a list of project dependencies')
    
    print('')
    print('- python3 main.py -ver')
    print('Get version')


elif mode_flag == '-m':
    import imageio
    from io import BytesIO
    video_path = args[1]
    video_file = open(video_path, 'rb')
    content = video_file.read()
    video = imageio.get_reader(BytesIO(content), 'ffmpeg', loop=True)
    print(json.dumps(video.get_meta_data()))

elif mode_flag == '-if':
    print(json.dumps(interpolators))

elif mode_flag == '-deps':
    print(json.dumps(dependencies))

elif mode_flag == '-ver':
    print(json.dumps(version))

else:
    print(f'Unknown mode-flag `{mode_flag}`, run `python3 main.py -h` for a usage guide')

exit(0)






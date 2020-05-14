import math
import time
import os
from Interpolator import InterpolatorDictionary
import cProfile

video_root = '../../Datasets/bigbuckbunny/'

video_paths = ['24fps/native.mkv', '30fps/native.mkv', '20fps/native.mkv']

interpolators = ['nearest', 'oversample', 'linear']


target_fps = 60

def get_video_out_path(video_path, interpolator):
    dir = f'../../Output/{video_path[:5]}'
    
    if not os.path.exists(dir):
        os.makedirs(dir)

    s = f'{dir}/{interpolator}.mkv'
    return s

for video_path in video_paths:
    for interpolator_str in interpolators:
        video_in_path = video_root + video_path
        video_out_path = get_video_out_path(video_path, interpolator_str)

        interpolator_obj = InterpolatorDictionary[interpolator_str]
        interpolator = interpolator_obj(target_fps, video_in_path, video_out_path, math.inf, 500)

        print(f'Processing {video_path} using {str(interpolator)}')
        interpolator.interpolate_video()

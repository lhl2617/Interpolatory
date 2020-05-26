import sys
import math
from ....Globals import debug_flags

from .base import BaseInterpolator

'''
%
%   e.g. 24->60
%   A A A B B C C C D D
%
%   e.g. 25->30
%   A A B C D E F
%
'''


class NearestInterpolator(BaseInterpolator):
    def __init__(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size)

    def get_interpolated_frame(self, idx):
        source_frame_idx = math.floor(idx / self.rate_ratio)

        if (debug_flags['debug_interpolator']):
            print(
                f'targetframe: {idx}, using source frame: {source_frame_idx}')

        return self.video_stream.get_frame(source_frame_idx)

    def __str__(self):
        return 'Nearest'
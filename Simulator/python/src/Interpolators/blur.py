import sys
import math
from ..Globals import debug_flags
import numpy as np
from .base import BaseInterpolator
from ..util import blend_frames

# blur the video by taking a window
# taken from https://github.com/laomao0/BIN/blob/master/data_scripts/adobe240fps/create_dataset_blur_N_frames_average.py

class BlurInterpolator(BaseInterpolator):
    def __init__(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size)

        self.inv_rate_ratio = None

        '''
        Only supports downscaling by integer amount, this is the 'window_size'
        '''
        if not (self.video_in_path is None):
            if self.rate_ratio > 1:
                raise Exception(f'{self.__str__()} only supports downconversion, got conversion rate ratio {self.rate_ratio}')
            inv_rate_ratio = 1. / self.rate_ratio
            if not (inv_rate_ratio.is_integer()):
                raise Exception(f'{self.__str__()} only supports integer downconversion, got downconversion ratio {inv_rate_ratio}')
            
            self.inv_rate_ratio = int(inv_rate_ratio)

            # to load the whole window at once
            self.video_stream.max_cache_size = self.inv_rate_ratio

    def get_interpolated_frame(self, idx):
        if (self.inv_rate_ratio is None):
            raise Exception(f'{self.__str__()} cannot be benchmarked as it is a downconversion method')
            
        start_frame_idx = idx * self.inv_rate_ratio

        frames_to_blend = [self.video_stream.get_frame(i) for i in range(start_frame_idx, start_frame_idx + self.inv_rate_ratio)]

        blended_frame = blend_frames(frames_to_blend)

        return blended_frame

    def __str__(self):
        return 'Blur'
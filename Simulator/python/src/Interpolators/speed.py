import sys
import math
from ..Globals import debug_flags

from .base import BaseInterpolator

'''
Just changes the speed of the video to match the frame rate
'''

class SpeedInterpolator(BaseInterpolator):
    def __init__(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=1, **args):
        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size, **args)

        self.max_frames_possible = self.video_stream.nframes

    def get_interpolated_frame(self, idx):
        return self.video_stream.get_frame(idx)
    
    def __str__(self):
        return 'Speed'
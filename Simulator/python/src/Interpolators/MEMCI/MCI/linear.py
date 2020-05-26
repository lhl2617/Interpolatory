import sys
import math
import imageio
import numpy as np
import sys
from io import BytesIO
from fractions import Fraction
from decimal import Decimal

from ....Globals import debug_flags
from ....util import blend_frames, get_first_frame_idx_and_ratio

from .base import BaseInterpolator
'''
%
%   e.g. 24->60 (rateRatio 2.5, period 5)
%   A (1.5A+B)/2.5 (0.5A+2B)/2.5 (2B+0.5C)/2.5 (B+1.5C)/2.5 
%
'''


class LinearInterpolator(BaseInterpolator):
    def __init__(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size)

    def get_interpolated_frame(self, idx):
        frameA_idx, weightA = get_first_frame_idx_and_ratio(idx, self.rate_ratio)
        frameB_idx = frameA_idx + 1

        frameA = self.video_stream.get_frame(frameA_idx)
        frameB = self.video_stream.get_frame(frameB_idx)

        weightB = 1. - weightA

        if (debug_flags['debug_interpolator']):
            print(
                f'targetframe: {idx}, using source frame: ({weightA} * {frameA_idx} + {weightB} * {frameB_idx}) / {self.rate_ratio}')

        weights = [weightA, weightB]
        frames = [frameA, frameB]

        output = blend_frames(frames, weights)

        return output

    def __str__(self):
        return 'Linear'


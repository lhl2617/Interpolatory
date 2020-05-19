import sys
import math
import imageio
import numpy as np
import sys
from io import BytesIO
from fractions import Fraction
from decimal import Decimal

from ..Globals import debug_flags
from ..util import blend_frames

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
        output = []

        # this period is the number of frame in the targetRate
        # before a cycle occurs (e.g. in the 24->60 case it occurs between B &
        # C at period = 5
        frac = Fraction(Decimal(self.rate_ratio))
        period = frac.numerator

        # which targetFrame is this after a period
        offset = math.floor(idx % period)

        # a key frame is a source frame that matches in time, this key frame
        # is the latest possible source frame
        key_frame_idx = math.floor(idx / period) * period

        rate_ratios_from_key_frame = math.floor(offset / self.rate_ratio)

        distance_from_prev_rate_ratio_point = offset - \
            (rate_ratios_from_key_frame) * self.rate_ratio

        frameA_idx = math.floor(
            key_frame_idx / self.rate_ratio + rate_ratios_from_key_frame)
        frameB_idx = frameA_idx + 1

        frameA = self.video_stream.get_frame(frameA_idx)
        frameB = self.video_stream.get_frame(frameB_idx)

        weightB = distance_from_prev_rate_ratio_point
        weightA = self.rate_ratio - weightB
        if (debug_flags['debug_interpolator']):
            print(
                f'targetframe: {idx}, using source frame: ({weightA} * {frameA_idx} + {weightB} * {frameB_idx}) / {self.rate_ratio}')

        weights = [weightA, weightB]
        frames = [frameA, frameB]

        output = blend_frames(frames, weights)

        return output

    def __str__(self):
        return 'linear'


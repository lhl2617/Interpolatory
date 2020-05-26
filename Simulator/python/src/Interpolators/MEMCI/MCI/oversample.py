import sys
import math
from fractions import Fraction
from decimal import Decimal

from ....Globals import debug_flags
from ....util import blend_frames

from .base import BaseInterpolator
'''
%
%   e.g. 24->60 (rateRatio 2.5, period 5)
%   A A (A+B)/2 B B C C (C+D)/2 E E
%
%   e.g. 25->30 (rateRatio 1.2, period 6)
%   A .2A+.8B .4B+.6C .6C+.4D .8D+.2E E F
%
'''


class OversampleInterpolator(BaseInterpolator):
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

        distance_from_next_rate_ratio_point = (
            rate_ratios_from_key_frame + 1) * self.rate_ratio - offset

        if distance_from_next_rate_ratio_point >= 1:
            frame_num = math.floor(
                key_frame_idx / self.rate_ratio + rate_ratios_from_key_frame)

            if (debug_flags['debug_interpolator']):
                print(f'targetframe: {idx}, using source frame: {frame_num}')

            output = self.video_stream.get_frame(frame_num)

        else:
            frameA_idx = math.floor(
                key_frame_idx / self.rate_ratio + rate_ratios_from_key_frame)
            frameB_idx = frameA_idx + 1

            frameA = self.video_stream.get_frame(frameA_idx)
            frameB = self.video_stream.get_frame(frameB_idx)

            weightA = distance_from_next_rate_ratio_point
            weightB = 1. - weightA

            weights = [weightA, weightB]
            frames = [frameA, frameB]

            if (debug_flags['debug_interpolator']):
                print(
                    f'targetframe: {idx}, using source frame: {weightA} * {frameA_idx} + {weightB} * {frameB_idx}')
            output = blend_frames(frames, weights)

        return output

    def __str__(self):
        return 'Oversample'

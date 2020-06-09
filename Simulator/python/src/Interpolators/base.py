import sys
import math
import numpy as np
import imageio
import time
from copy import deepcopy
from io import BytesIO
from fractions import Fraction
from decimal import Decimal
from ..util import sToMMSS, getETA, signal_progress, is_power_of_two, blend_frames
from ..Globals import debug_flags
from ..VideoStream import BenchmarkVideoStream, VideoStream

'''
Base Interpolator object for implemented interpolators to derive from.

video_in_path and video_out_path are optional, for example when benchmarking we do not need video files
'''


class BaseInterpolator(object):
    def __init__(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=0, **args):
        self.target_fps = target_fps
        self.video_in_path = video_in_path
        self.video_out_path = video_out_path
        self.max_out_frames = max_out_frames
        self.max_cache_size = max_cache_size
        self.video_stream = None
        self.video_out_writer = None


        self.max_frames_possible = None
        self.rate_ratio = None

        if not (video_in_path is None):
            self.load_input_video()

        if not (video_out_path is None):
            self.get_video_out_writer()

        for arg, value in args.items():
            setattr(self, arg, value)

    def load_input_video(self):
        if self.video_in_path is None:
            raise Exception('video input path not given')

        file = open(self.video_in_path, 'rb')
        content = file.read()
        # loop=True solves reading beyond last index, it wraps around
        vid = imageio.get_reader(BytesIO(content), 'ffmpeg', loop=True)

        if (debug_flags['debug_IO']):
            print(f'Loaded input video from {self.video_in_path}.')
            print(vid.get_meta_data())

        self.video_stream = VideoStream(vid, self.max_cache_size)

        # maximum frames possible according to target_fps
        self.max_frames_possible = math.floor(
            self.video_stream.duration * self.target_fps)
        self.rate_ratio = self.target_fps / self.video_stream.fps

    def get_video_out_writer(self):
        if self.video_out_path is None:
            raise Exception('video output path not given')


            '''
            See bottom of file for options
            '''
        self.video_out_writer = imageio.get_writer(
            self.video_out_path, fps=self.target_fps, macro_block_size=0, quality=6)


    def interpolate_video(self):
        if self.video_in_path is None or self.video_out_path is None:
            raise Exception(
                'Cannot interpolate video, no input video path or output video path')


        start = int(round(time.time()))

        # target number of frames is limited by max possible according to source
        target_nframes = min(self.max_frames_possible, self.max_out_frames)

        for i in range(target_nframes):
            # if (debug_flags['debug_progress']):
            if ((i % self.target_fps) == 0):
                pct = str(math.floor(100 * (i+1) / target_nframes)).rjust(3, ' ')
                curr = int(round(time.time()))
                elapsed_seconds = int((curr-start))
                elapsed = sToMMSS(elapsed_seconds)
                eta = getETA(elapsed_seconds, i, target_nframes)
                progStr = f'PROGRESS::{pct}%::Frame {i}/{target_nframes} | Time elapsed: {elapsed} | Estimated Time Left: {eta}'
                signal_progress(progStr)

                if (debug_flags['debug_progress']):
                    print(progStr)

            interpolated_frame = self.get_interpolated_frame(i)
            self.video_out_writer.append_data(interpolated_frame)

        self.video_out_writer.close()

        end = int(round(time.time()))

        # if (debug_flags['debug_timer']):
        elapsed = sToMMSS(int((end-start)))
        progStr = f'PROGRESS::100%::Complete | Time taken: {sToMMSS((end-start))}'
        signal_progress(progStr)
        if (debug_flags['debug_progress']):
            print(progStr)


    def get_interpolated_frame(self, idx):
        raise NotImplementedError('To be implemented by derived classes')

    def __str__(self):
        raise NotImplementedError('To be implemented by derived classes')


    '''
    For benchmarking, this returns the assumed 'middle' frame given image_1 and image_2.

    The idea is that we treat the input as a 2s 1fps video_stream (by populating VideoStream)
    Then, we set target_fps to 2 and get the frame at index 1

    video_stream now contains benchmark_video_stream

    this is used by interpolators that are not limited
    '''

    def get_benchmark_frame(self, image_1, image_2):
        # so that we can restore to defaults
        backup_interpolator = deepcopy(self)

        # replace with Benchmark video_stream
        self.MV_field_idx = -1
        self.video_stream = BenchmarkVideoStream(image_1, image_2)
        self.target_fps = 2
        self.max_out_frames = 2

        self.rate_ratio = 2.
        self.max_frames_possible = 2

        # clear cache for MidFrame
        self.clear_cache()

        res = self.get_interpolated_frame(1)

        # restore
        self = backup_interpolator

        return res

    def clear_cache(self):
        # used for MidFrameBaseInterpolator to inherit and clear cache
        pass

class MidFrameBaseInterpolator(BaseInterpolator):
    '''
    This is a base class for ML implementations or methods that only support mid frame interpolation (e.g. SepConv)
    '''
    def __init__(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):

        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size)

        # denominator is 2
        self.den2 = False

        '''
        Only supports upscaling by factor of 2 or
        if the factor has denominator 2
        by blurring the output
        (this is mainly to support 24->60 by doing 24->120->60)
        '''
        if not (self.video_in_path is None):
            if self.rate_ratio < 1:
                raise Exception(f'{self.__str__()} only supports upconversion, got conversion rate ratio {self.rate_ratio}')

            from fractions import Fraction
            from decimal import Decimal

            frac = Fraction(Decimal(self.rate_ratio))
            denominator = frac.denominator

            if (not is_power_of_two(self.rate_ratio)) and denominator != 2:
                raise Exception(f'{self.__str__()} only supports upconversion ratio that is a power of 2 OR has denominator 2 (e.g. 2.5 = 5/2), got conversion rate ratio {self.rate_ratio}')

            if denominator == 2:
                self.den2 = True
                # we now need to double the target fps
                self.target_fps *= 2
                # and also rate_ratio
                self.rate_ratio = int(self.rate_ratio * 2)

        '''
        we store rate_ratio interpolated frames in cache
        '''
        self.cache = {}

    def get_middle_frame(self, image_1, image_2):
        # get middle frame
        raise NotImplementedError('To be implemented by derived classes')

    # WARNING: the first top level recursive call must be a valid group of images
    # i.e. the LHS and RHS must correspond to real frames in the original video
    def repopulate_cache(self, image_1_idx, image_2_idx):
        '''
        gets the middle frame given two images then populates __sepconv_cache
        recursively call until populated

        assumes image_1 and image_2 already in cache
        '''
        if (image_1_idx + 1 == image_2_idx):
            return

        # assumes the two frames image_1 and image_2 are already in cache
        image_1 = self.cache[image_1_idx]
        image_2 = self.cache[image_2_idx]

        mid_image = self.get_middle_frame(image_1, image_2)
        mid_image_idx = int((image_1_idx + image_2_idx) / 2)

        self.cache[mid_image_idx] = mid_image

        # LHS
        self.repopulate_cache(image_1_idx, mid_image_idx)
        # RHS
        self.repopulate_cache(mid_image_idx, image_2_idx)

    def get_interpolated_frame(self, idx):
        if self.den2:
            # denominator 2 case
            true_idx = idx * 2

            if not (true_idx in self.cache):
                self.cache.clear()

                # repopulate cache
                image_1_idx = int(true_idx)
                image_2_idx = int(true_idx + self.rate_ratio)

                # put the relevant frames in cache first
                frameA_idx = true_idx // self.rate_ratio
                frameB_idx = frameA_idx + 1
                frameA = self.video_stream.get_frame(int(frameA_idx))
                frameB = self.video_stream.get_frame(int(frameB_idx))
                self.cache[image_1_idx] = frameA
                self.cache[image_2_idx] = frameB

                self.repopulate_cache(image_1_idx, image_2_idx)

            blend_1 = self.cache[true_idx]
            blend_2 = self.cache[true_idx + 1]

            blended_frame = blend_frames([blend_1, blend_2])

            return blended_frame

        else:
            # normal case
            # if not found in cache
            if not (idx in self.cache):
                self.cache.clear()

                # repopulate cache
                image_1_idx = int(idx // self.rate_ratio * self.rate_ratio)
                image_2_idx = int(image_1_idx + self.rate_ratio)

                # put the relevant frames in cache first
                frameA_idx = idx // self.rate_ratio

                frameB_idx = frameA_idx + 1
                frameA = self.video_stream.get_frame(int(frameA_idx))
                frameB = self.video_stream.get_frame(int(frameB_idx))
                self.cache[image_1_idx] = frameA
                self.cache[image_2_idx] = frameB

                self.repopulate_cache(image_1_idx, image_2_idx)

            return self.cache[idx]

    def clear_cache(self):
        self.cache.clear()

'''
Parameters for saving
    ---------------------
    fps : scalar
        The number of frames per second. Default 10.
    codec : str
        the video codec to use. Default 'libx264', which represents the
        widely available mpeg4. Except when saving .wmv files, then the
        defaults is 'msmpeg4' which is more commonly supported for windows
    quality : float | None
        Video output quality. Default is 5. Uses variable bit rate. Highest
        quality is 10, lowest is 0. Set to None to prevent variable bitrate
        flags to FFMPEG so you can manually specify them using output_params
        instead. Specifying a fixed bitrate using 'bitrate' disables this
        parameter.
    bitrate : int | None
        Set a constant bitrate for the video encoding. Default is None causing
        'quality' parameter to be used instead.  Better quality videos with
        smaller file sizes will result from using the 'quality'  variable
        bitrate parameter rather than specifiying a fixed bitrate with this
        parameter.
    pixelformat: str
        The output video pixel format. Default is 'yuv420p' which most widely
        supported by video players.
    input_params : list
        List additional arguments to ffmpeg for input file options (i.e. the
        stream that imageio provides).
    output_params : list
        List additional arguments to ffmpeg for output file options.
        (Can also be provided as ``ffmpeg_params`` for backwards compatibility)
        Example ffmpeg arguments to use only intra frames and set aspect ratio:
        ['-intra', '-aspect', '16:9']
    ffmpeg_log_level: str
        Sets ffmpeg output log level.  Default is "warning".
        Values can be "quiet", "panic", "fatal", "error", "warning", "info"
        "verbose", or "debug". Also prints the FFMPEG command being used by
        imageio if "info", "verbose", or "debug".
    macro_block_size: int
        Size constraint for video. Width and height, must be divisible by this
        number. If not divisible by this number imageio will tell ffmpeg to
        scale the image up to the next closest size
        divisible by this number. Most codecs are compatible with a macroblock
        size of 16 (default), some can go smaller (4, 8). To disable this
        automatic feature set it to None or 1, however be warned many players
        can't decode videos that are odd in size and some codecs will produce
        poor results or fail. See https://en.wikipedia.org/wiki/Macroblock.
    '''

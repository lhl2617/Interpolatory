import sys
import math
import numpy as np
import imageio
import time
from copy import deepcopy
from io import BytesIO
from fractions import Fraction
from decimal import Decimal
from ..util import sToMMSS, getETA, signal_progress
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


        start = int(round(time.time() * 1000))

        # target number of frames is limited by max possible according to source
        target_nframes = min(self.max_frames_possible, self.max_out_frames)

        for i in range(target_nframes):
            # if (debug_flags['debug_progress']):
            if ((i % self.target_fps) == 0):
                pct = str(math.floor(100 * (i+1) / target_nframes)).rjust(3, ' ')
                curr = int(round(time.time() * 1000))
                elapsed_seconds = int((curr-start) / 1000)
                elapsed = sToMMSS(elapsed_seconds)
                eta = getETA(elapsed_seconds, i, target_nframes)
                progStr = f'PROGRESS::{pct}%::Frame {i}/{target_nframes} | Time elapsed: {elapsed} | Estimated Time Left: {eta}'
                signal_progress(progStr)

                if (debug_flags['debug_progress']):
                    print(progStr)
                    
            interpolated_frame = self.get_interpolated_frame(i)
            self.video_out_writer.append_data(interpolated_frame)

        self.video_out_writer.close()

        end = int(round(time.time() * 1000))

        # if (debug_flags['debug_timer']):
        elapsed = sToMMSS(int((end-start) / 1000))
        progStr = f'PROGRESS::100%::Complete | Time taken: {sToMMSS((end-start) / 1000)}'
        signal_progress(progStr)
        if (debug_flags['debug_progress']):
            print(progStr)
        

    def get_interpolated_frame(self, idx):
        raise NotImplementedError('To be implemented by derived classes')
        return []

    def __str__(self):
        raise ExcepNotImplementedErrortion('To be implemented by derived classes')


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
        self.video_stream = BenchmarkVideoStream(image_1, image_2)
        self.target_fps = 2
        self.max_out_frames = 2
        self.rate_ratio = 2.
        self.max_frames_possible = 2

        res = self.get_interpolated_frame(1)

        # restore
        self = backup_interpolator

        return res


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
    
import imageio
import math
import time
import numpy as np
from io import BytesIO
from fractions import Fraction
from .ME.full_search import get_motion_vectors as get_motion_vectors_fs
from .ME.tss import get_motion_vectors as get_motion_vectors_tss
from decimal import Decimal
from copy import deepcopy
# from Globals import debug_flags
# from VideoStream import BenchmarkVideoStream, VideoStream
import matplotlib.pyplot as plt
from .smoothing.threeXthree_mv_smoothing import smooth
from .smoothing.median_filter import median_filter
from .smoothing.mean_filter import mean_filter
from .smoothing.weighted_mean_filter import weighted_mean_filter
from .ME.hbma import get_motion_vectors as hbma
from ..base import BaseInterpolator
'''
blends frames
'''


def blend_frames(frames, weights):
    return np.average(frames, axis=0, weights=weights).astype(np.uint8, copy=False)


'''
Base Interpolator object for implemented interpolators to derive from.

video_in_path and video_out_path are optional, for example when benchmarking we do not need video files
'''


# class BaseInterpolator:
#     def __init__(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=0, **args):
#         self.target_fps = target_fps
#         self.video_in_path = video_in_path
#         self.video_out_path = video_out_path
#         self.max_out_frames = max_out_frames
#         self.max_cache_size = max_cache_size
#         self.video_stream = None
#         self.video_out_writer = None
#
#         self.MV_field_idx= -1 #Index in source video that the current motion field is based on.
#         self.MV_field=[]
#
#         self.max_frames_possible = None
#         self.rate_ratio = None
#
#         if not (video_in_path is None):
#             self.load_input_video()
#
#         if not (video_out_path is None):
#             self.get_video_out_writer()
#
#         for arg, value in args.items():
#             setattr(self, arg, value)
#
#     def load_input_video(self):
#         if self.video_in_path is None:
#             raise Exception('video input path not given')
#
#         file = open(self.video_in_path, 'rb')
#         content = file.read()
#         # loop=True solves reading beyond last index, it wraps around
#         vid = imageio.get_reader(BytesIO(content), 'ffmpeg', loop=True)
#
#         if (debug_flags['debug_IO']):
#             print(f'Loaded input video from {self.video_in_path}.')
#             print(vid.get_meta_data())
#
#         self.video_stream = VideoStream(vid, self.max_cache_size)
#
#         # maximum frames possible according to target_fps
#         self.max_frames_possible = math.floor(
#             self.video_stream.duration * self.target_fps)
#         self.rate_ratio = self.target_fps / self.video_stream.fps
#
#     def get_video_out_writer(self):
#         if self.video_out_path is None:
#             raise Exception('video output path not given')
#
#
#             '''
#             See bottom of file for options
#             '''
#         self.video_out_writer = imageio.get_writer(
#             self.video_out_path, fps=self.target_fps, macro_block_size=0, quality=6)
#
#
#     def interpolate_video(self,b,t):
#         if self.video_in_path is None or self.video_out_path is None:
#             raise Exception(
#                 'Cannot interpolate video, no input video path or output video path')
#
#
#         start = int(round(time.time() * 1000))
#
#         # target number of frames is limited by max possible according to source
#         target_nframes = min(self.max_frames_possible, self.max_out_frames)
#
#         for i in range(target_nframes):
#
#             if (debug_flags['debug_progress']):
#                 if ((i % self.target_fps) == 0):
#                     print(f'{i}/{target_nframes} | {100 * i / target_nframes} %')
#
#             interpolated_frame = self.get_interpolated_frame(i,b,t)
#             self.video_out_writer.append_data(interpolated_frame)
#
#         self.video_out_writer.close()
#
#         end = int(round(time.time() * 1000))
#
#         if (debug_flags['debug_timer']):
#             print(f'Took {(end-start) / 1000} seconds')
#
#     def get_interpolated_frame(self, idx, b, t):
#         raise Exception('To be implemented by derived classes')
#         return []
#
#     def __str__(self):
#         raise Exception('To be implemented by derived classes')
#

'''
    For benchmarking, this returns the assumed 'middle' frame given image_1 and image_2.

    The idea is that we treat the input as a 2s 1fps video_stream (by populating VideoStream)
    Then, we set target_fps to 2 and get the frame at index 1

    video_stream now contains benchmark_video_stream
'''
    #
    # def get_benchmark_frame(self, image_1, image_2, b ,t):
    #     # so that we can restore to defaults
    #     backup_interpolator = deepcopy(self)
    #
    #     # replace with Benchmark video_stream
    #     self.video_stream = BenchmarkVideoStream(image_1, image_2)
    #     self.target_fps = 2
    #     self.max_out_frames = 2
    #     self.rate_ratio = 2.
    #     self.max_frames_possible = 2
    #
    #     res = self.get_interpolated_frame(1,b,t)
    #
    #     # restore
    #     self = backup_interpolator
    #
    #     return res
    #

'''
MEMCI using full search for ME and uniderictional
MCI with median filter for filling holes.



'''

class MEMCIInterpolator(BaseInterpolator):
    def __init___(self, target_fps,video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):

        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size)


    def get_interpolated_frame(self, idx,**args):
        self.blockSize = 8 #args["blockSize"]
        self.target_region = 3 #args["target_region"]
        self.ME_method = ME_dict["tss"]#args["ME_method"]
        self.smoothing_filter = smoothing_dict["weighted"]#args["smoothing_filter"]#
        self.filterSize = 5 #args["filterSize"]

        for arg, value in args.items():
            setattr(self, arg, value)
        print("the block size used was:", self.blockSize)
    # def get_interpolated_frame(self, idx, b, t):
        #source_frame is the previous frame in the source vidoe.
        source_frame_idx = math.floor(idx/self.rate_ratio)
        source_frame = self.video_stream.get_frame(source_frame_idx)
        print(source_frame_idx)
        #Normalized distance from current_frame to the source frame.
        dist = idx/self.rate_ratio - math.floor(idx/self.rate_ratio)

        #If the frame to be interpolated is coinciding with a source frame.
        if dist == 0:
            return source_frame


        #Check if the frame to be interpolated is between the two frames
        #that the current motion field is estimated on.
        if not self.MV_field_idx < idx/self.rate_ratio < self.MV_field_idx+1:
            target_frame = self.video_stream.get_frame(source_frame_idx+1)
            self.MV_field= self.ME_method(self.blockSize,self.target_region,source_frame,target_frame)

            # block_size = 16
            # region = 7
            sub_region =1
            steps_HBMA = 1
            min_block_size = 2
            # self.MV_field = hbma(b,t,sub_region,steps_HBMA,min_block_size,source_frame,target_frame)
            # print("Begin smoothing")
            self.MV_field = smooth(self.smoothing_filter,self.MV_field,self.filterSize)
            self.MV_field_idx = source_frame_idx


            #Uncomment if you want to plot vector field when running benchmark.py
            #self.plot_vector_field(block_size,steps, source_frame)




        #Initialize new frame
        Interpolated_Frame =  np.ones(source_frame.shape)*-1
        #Matrix with lowest sad value fo every interpolated pixel.
        SAD_interpolated_frame = np.full([source_frame.shape[0],source_frame.shape[1]],np.inf)

        #Follow motion vectorcs to obtain interpolated pixel Values
        #If interpolated frame has multiple values, take the one with lowest SAD.
        for u in range(0, source_frame.shape[0]):
            for v in range(0, source_frame.shape[1]):

                #Get the new coordinates by following scaled MV.
                u_i = int(u + round(self.MV_field[u,v,0]*dist))
                v_i = int(v + round(self.MV_field[u,v,1]*dist))
                # print("u_i ",u_i," v_i ",v_i)
                if(u_i<source_frame.shape[0] and v_i<source_frame.shape[1]):
                    if  self.MV_field[u,v,2] <= SAD_interpolated_frame[u_i, v_i]:

                        Interpolated_Frame[u_i, v_i] =  source_frame[u, v]
                        SAD_interpolated_frame[u_i, v_i] = self.MV_field[u,v,2]

        # New_Interpolated_Frame = smooth(mean_filter, self.MV_field, 10)

        #Run median filter over empty pixels in the interpolated frame.
        k=10 #Median filter size = (2k+1)x(2k+1)
        #Bad implementation. Did not find any 3d median filter
        # that can be applied to specific pixels.
        New_Interpolated_Frame = np.copy(Interpolated_Frame)
        for u in range(0, Interpolated_Frame.shape[0]):
            for v in range(0, Interpolated_Frame.shape[1]):
                if Interpolated_Frame[u,v,0] == -1:
                    u_min=max(0,u-k)
                    u_max=min(Interpolated_Frame.shape[0],u+k+1)
                    v_min=max(0,v-k)
                    v_max=min(Interpolated_Frame.shape[1],v+k+1)
                    New_Interpolated_Frame[u,v,0] = np.median(Interpolated_Frame[u_min:u_max,v_min:v_max,0])
                    New_Interpolated_Frame[u,v,1] = np.median(Interpolated_Frame[u_min:u_max,v_min:v_max,1])
                    New_Interpolated_Frame[u,v,2] = np.median(Interpolated_Frame[u_min:u_max,v_min:v_max,2])

        New_Interpolated_Frame = New_Interpolated_Frame.astype(source_frame.dtype)

        # print(self.filterSize,self.smoothing_filter,self.ME_method,self.target_region,self.blockSize)
        return New_Interpolated_Frame
'''
%
%   e.g. 24->60
%   A A A B B C C    C D D
%
%   e.g. 25->30
%   A A B C D E F
%
'''


class Bi(BaseInterpolator):
    def __init___(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2,
                  **args):
        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size)

    def get_interpolated_frame(self, idx):

        source_frame_idx = math.floor(idx / self.rate_ratio)
        source_frame = self.video_stream.get_frame(source_frame_idx)

        dist = idx / self.rate_ratio - math.floor(idx / self.rate_ratio)

        if dist == 0:
            return source_frame

        if not self.MV_field_idx < idx / self.rate_ratio < self.MV_field_idx + 1:
            target_frame = self.video_stream.get_frame(source_frame_idx + 1)
            # self.MV_field = get_motion_vectors(4, 10, source_frame, target_frame)
            self.MV_field_idx = source_frame_idx

            '''
            fwd = get_motion_vectors(4, 10, source_frame, target_frame)
            bwd = get_motion_vectors(4, 10, target_frame, source_frame)

            if fwd[,,2]>bwd[,,2]: #use the one with smaller SAD
                self.MV_field = bwd
                dist = 1 - dist
            else :
                self.MV_field = fwd

            self.MV_field_idx = source_frame_idx
            '''
            fwd = get_motion_vectors_tss(4, 3, source_frame, target_frame)
            bwd = get_motion_vectors_tss(4, 3, target_frame, source_frame)
            self.MV_field = fwd
        Interpolated_Frame = np.ones(source_frame.shape, dtype='float64') * -1
        SAD_interpolated_frame = np.full([source_frame.shape[0], source_frame.shape[1]], np.inf)

        for u in range(0, source_frame.shape[0]):
            for v in range(0, source_frame.shape[1]):
                if fwd[u, v, 2] > bwd[u, v, 2]:
                    dist = 1.0 - dist
                    u_i = int(u + round(bwd[u, v, 0] * dist))
                    v_i = int(v + round(bwd[u, v, 1] * dist))

                    if bwd[u, v, 2] <= SAD_interpolated_frame[u_i, v_i]:
                        Interpolated_Frame[u_i, v_i] = source_frame[u, v]
                        SAD_interpolated_frame[u_i, v_i] = bwd[u, v, 2]
                        self.MV_field[u, v] = bwd[u, v]

                        # self.MV_field[u,v,0] = bwd[u,v,0]
                        # self.MV_field[u,v,1] = bwd[u,v,1]
                        # self.MV_field[u,v,2] = bwd[u,v,2]

                else:
                    u_i = int(u + round(fwd[u, v, 0] * dist))
                    v_i = int(v + round(fwd[u, v, 1] * dist))

                    if fwd[u, v, 2] <= SAD_interpolated_frame[u_i, v_i]:
                        Interpolated_Frame[u_i, v_i] = source_frame[u, v]
                        SAD_interpolated_frame[u_i, v_i] = fwd[u, v, 2]

        k = 5  # Median filter size = (2k+1)x(2k+1)
        for u in range(0, Interpolated_Frame.shape[0]):
            for v in range(0, Interpolated_Frame.shape[1]):
                if Interpolated_Frame[u, v, 0] == -1:
                    u_min = max(0, u - k)
                    u_max = min(Interpolated_Frame.shape[0], u + k + 1)
                    v_min = max(0, v - k)
                    v_max = min(Interpolated_Frame.shape[1], v + k + 1)
                    Interpolated_Frame[u, v, 0] = np.median(Interpolated_Frame[u_min:u_max, v_min:v_max, 0])
                    Interpolated_Frame[u, v, 1] = np.median(Interpolated_Frame[u_min:u_max, v_min:v_max, 1])
                    Interpolated_Frame[u, v, 2] = np.median(Interpolated_Frame[u_min:u_max, v_min:v_max, 2])

        return Interpolated_Frame

    def __str__(self):
        return 'BI'

# class NearestInterpolator(BaseInterpolator):
#     def __init___(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
#         super().__init__(target_fps, video_in_path,
#                          video_out_path, max_out_frames, max_cache_size)
#
#     def get_interpolated_frame(self, idx):
#         source_frame_idx = math.floor(idx / self.rate_ratio)
#
#         if (debug_flags['debug_interpolator']):
#             print(
#                 f'targetframe: {idx}, using source frame: {source_frame_idx}')
#
#         return self.video_stream.get_frame(source_frame_idx)
#
#     def __str__(self):
#         return 'nearest'


'''
%
%   e.g. 24->60 (rateRatio 2.5, period 5)
%   A A (A+B)/2 B B C C (C+D)/2 E E
%
%   e.g. 25->30 (rateRatio 1.2, period 6)
%   A .2A+.8B .4B+.6C .6C+.4D .8D+.2E E F
%
'''


# class OversampleInterpolator(BaseInterpolator):
#     def __init___(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
#         super().__init__(target_fps, video_in_path,
#                          video_out_path, max_out_frames, max_cache_size)
#
#     def get_interpolated_frame(self, idx):
#
#         output = []
#         # this period is the number of frame in the targetRate
#         # before a cycle occurs (e.g. in the 24->60 case it occurs between B &
#         # C at period = 5
#         frac = Fraction(Decimal(self.rate_ratio))
#         period = frac.numerator
#
#         # which targetFrame is this after a period
#         offset = math.floor(idx % period)
#
#         # a key frame is a source frame that matches in time, this key frame
#         # is the latest possible source frame
#         key_frame_idx = math.floor(idx / period) * period
#
#         rate_ratios_from_key_frame = math.floor(offset / self.rate_ratio)
#
#         distance_from_next_rate_ratio_point = (
#             rate_ratios_from_key_frame + 1) * self.rate_ratio - offset
#
#         if distance_from_next_rate_ratio_point >= 1:
#             frame_num = math.floor(
#                 key_frame_idx / self.rate_ratio + rate_ratios_from_key_frame)
#
#             if (debug_flags['debug_interpolator']):
#                 print(f'targetframe: {idx}, using source frame: {frame_num}')
#
#             output = self.video_stream.get_frame(frame_num)
#         else:
#             frameA_idx = math.floor(
#                 key_frame_idx / self.rate_ratio + rate_ratios_from_key_frame)
#             frameB_idx = frameA_idx + 1
#
#             frameA = self.video_stream.get_frame(frameA_idx)
#             frameB = self.video_stream.get_frame(frameB_idx)
#
#             weightA = distance_from_next_rate_ratio_point
#             weightB = 1. - weightA
#
#             weights = [weightA, weightB]
#             frames = [frameA, frameB]
#
#             if (debug_flags['debug_interpolator']):
#                 print(
#                     f'targetframe: {idx}, using source frame: {weightA} * {frameA_idx} + {weightB} * {frameB_idx}')
#             output = blend_frames(frames, weights)
#
#         return output
#
#     def __str__(self):
#         return 'oversample'
#

'''
%
%   e.g. 24->60 (rateRatio 2.5, period 5)
%   A (1.5A+B)/2.5 (0.5A+2B)/2.5 (2B+0.5C)/2.5 (B+1.5C)/2.5
%
'''


# class LinearInterpolator(BaseInterpolator):
#     def __init___(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
#         super().__init__(target_fps, video_in_path,
#                          video_out_path, max_out_frames, max_cache_size)
#
#     def get_interpolated_frame(self, idx):
#         output = []
#
#         # this period is the number of frame in the targetRate
#         # before a cycle occurs (e.g. in the 24->60 case it occurs between B &
#         # C at period = 5
#         frac = Fraction(Decimal(self.rate_ratio))
#         period = frac.numerator
#
#         # which targetFrame is this after a period
#         offset = math.floor(idx % period)
#
#         # a key frame is a source frame that matches in time, this key frame
#         # is the latest possible source frame
#         key_frame_idx = math.floor(idx / period) * period
#
#         rate_ratios_from_key_frame = math.floor(offset / self.rate_ratio)
#
#         distance_from_prev_rate_ratio_point = offset - \
#             (rate_ratios_from_key_frame) * self.rate_ratio
#
#         frameA_idx = math.floor(
#             key_frame_idx / self.rate_ratio + rate_ratios_from_key_frame)
#         frameB_idx = frameA_idx + 1
#
#         frameA = self.video_stream.get_frame(frameA_idx)
#         frameB = self.video_stream.get_frame(frameB_idx)
#
#         weightB = distance_from_prev_rate_ratio_point
#         weightA = self.rate_ratio - weightB
#         if (debug_flags['debug_interpolator']):
#             print(
#                 f'targetframe: {idx}, using source frame: ({weightA} * {frameA_idx} + {weightB} * {frameB_idx}) / {self.rate_ratio}')
#
#         weights = [weightA, weightB]
#         frames = [frameA, frameB]
#
#         output = blend_frames(frames, weights)
#
#         return output
#
#     def __str__(self):
#         return 'linear'

#
# InterpolatorDictionary = {
#     'MEMCI' : MEMCIInterpolator
#     # 'BI':Bi
#     #'nearest': NearestInterpolator,
#     #'oversample': OversampleInterpolator,
#     #'linear': LinearInterpolator
# }



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

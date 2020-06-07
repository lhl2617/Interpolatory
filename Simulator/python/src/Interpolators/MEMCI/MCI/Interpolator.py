import imageio
import math
import time
import numpy as np
from io import BytesIO
from fractions import Fraction
import scipy
import sys

from ....util import eprint

sys.path.append('.')

from ..ME.full_search import get_motion_vectors as fs
from ..ME.tss import get_motion_vectors as tss
from decimal import Decimal
from copy import deepcopy
# from Globals import debug_flags
# from VideoStream import BenchmarkVideoStream, VideoStream
import matplotlib.pyplot as plt
from ..smoothing.threeXthree_mv_smoothing import smooth
from ..smoothing.median_filter import median_filter
from ..smoothing.mean_filter import mean_filter
from ..smoothing.weighted_mean_filter import weighted_mean_filter
from ..ME.hbma import get_motion_vectors as hbma
from ...base import BaseInterpolator
from .Unidirectional_2 import UniDir2Interpolator
'''
blends frames
'''


def blend_frames(frames, weights):
    return np.average(frames, axis=0, weights=weights).astype(np.uint8, copy=False)

'''
MEMCI using full search for ME and uniderictional
MCI with median filter for filling holes.



'''
ME_dict={
    "full":fs,
    "tss":tss,
    "HBMA":hbma,
}
smoothing_dict={
    "mean":mean_filter,
    "median":median_filter,
    "weighted":weighted_mean_filter

}
class UniDirInterpolator(BaseInterpolator):
    def __init__(self, target_fps,video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size)

        self.block_size = 8
        # print('sup bro set block_size here')
        # self.blockSize = block_size
        self.target_region = 7
        self.me_mode = ME_dict["HBMA"]
        # print(self.me_mode)
        self.filter_mode = smoothing_dict["weighted"]
        self.filterSize = 4
        self.sub_region = 1
        self.steps = 4
        self.min_block_size = 4

        if 'block_size' in args.keys():
            self.block_size = int(args['block_size'])
        if 'target_region' in args.keys():
            self.region = int(args['target_region'])
        if 'me_mode' in args.keys():
            self.me_mode = ME_dict[ args['me_mode']]
            if self.me_mode == tss:
                self.region = self.steps
    ### this function should be only self, idx, like in BaseInterpolator
    def get_interpolated_frame(self, idx):

        self.MV_field_idx= -1 #Index in source video that the current motion field is based on.
        self.MV_field=[]
        #for arg, value in args.items():
         #   setattr(self, arg, value)
        #print("the block size used was:", self.blockSize)
    # def get_interpolated_frame(self, idx, b, t):
        #source_frame is the previous frame in the source vidoe.
        source_frame_idx = math.floor(idx/self.rate_ratio)
        source_frame = self.video_stream.get_frame(source_frame_idx)
        #print(source_frame_idx)
        #Normalized distance from current_frame to the source frame.
        dist = idx/self.rate_ratio - math.floor(idx/self.rate_ratio)

        #If the frame to be interpolated is coinciding with a source frame.
        if dist == 0:
            return source_frame


        #Check if the frame to be interpolated is between the two frames
        #that the current motion field is estimated on.
        if not self.MV_field_idx < idx/self.rate_ratio < self.MV_field_idx+1:
            target_frame = self.video_stream.get_frame(source_frame_idx+1)
            # print(self.me_mode)
            if(self.me_mode!=hbma):

                # self.me_mode = ME_dict[self.me_mode]
                self.MV_field= self.me_mode(self.block_size,self.target_region,source_frame,target_frame)
            else:
                min_side = min(source_frame.shape[0],source_frame.shape[1])
                step_size=1
                while(min_side>255):
                    min_side/=2
                    step_size+=1
                self.steps=step_size
                self.MV_field= self.me_mode(self.block_size,self.target_region,self.sub_region,self.steps,self.min_block_size,source_frame,target_frame)

            # print("Begin smoothing")
            self.MV_field = smooth(self.filter_mode,self.MV_field,self.filterSize)
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
                else:
                    Interpolated_Frame[u, v] = source_frame[u, v]
                    SAD_interpolated_frame[u, v] = self.MV_field[u, v, 2]

        # New_Interpolated_Frame = smooth(mean_filter, self.MV_field, 10)
        #Run median filter over empty pixels in the interpolated frame.
        k=10 #Median filter size = (2k+1)x(2k+1)
        #Bad implementation. Did not find any 3d median filter
        # that can be applied to specific pixels.
        New_Interpolated_Frame = np.copy(Interpolated_Frame)
        for u in range(0, Interpolated_Frame.shape[0]):
            for v in range(0, Interpolated_Frame.shape[1]):
                if Interpolated_Frame[u,v,0] == -1:
                    #to make sure the hole is not empty
                    Interpolated_Frame[u, v] = source_frame[u, v]
                    SAD_interpolated_frame[u, v] = self.MV_field[u, v, 2]

                    u_min=max(0,u-k)
                    u_max=min(Interpolated_Frame.shape[0],u+k+1)
                    v_min=max(0,v-k)
                    v_max=min(Interpolated_Frame.shape[1],v+k+1)
                    New_Interpolated_Frame[u,v,0] = np.median(Interpolated_Frame[u_min:u_max,v_min:v_max,0])
                    New_Interpolated_Frame[u,v,1] = np.median(Interpolated_Frame[u_min:u_max,v_min:v_max,1])
                    New_Interpolated_Frame[u,v,2] = np.median(Interpolated_Frame[u_min:u_max,v_min:v_max,2])

        New_Interpolated_Frame = New_Interpolated_Frame.astype(source_frame.dtype)

        # print(self.filterSize,self.smoothing_filter,self.me_mode,self.target_region,self.blockSize)
        return New_Interpolated_Frame
    def __str__(self):
        return 'uniMEMCI'




'''
%
%   e.g. 24->60
%   A A A B B C C    C D D
%
%   e.g. 25->30
%   A A B C D E F
%
'''



# class Bi(BaseInterpolator):
#     def __init___(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2,
#                   **args):
#         super().__init__(target_fps, video_in_path,
#                          video_out_path, max_out_frames, max_cache_size)

    # def get_interpolated_frame(self, idx):
    #     self.blockSize = int(block_size)
    #     self.target_region = int(target_region)
    #     self.me_mode = ME_dict[ME_mode]
    #     self.smoothing_filter = smoothing_dict[filter_mode]
    #     self.filterSize = int(filter_size)
    #
    #
    #     self.MV_field_idx= -1 #Index in source video that the current motion field is based on.
    #     self.MV_field=[]
    #     #for arg, value in args.items():
    #     #    setattr(self, arg, value)
    #     source_frame_idx = math.floor(idx / self.rate_ratio)
    #     source_frame = self.video_stream.get_frame(source_frame_idx)
    #
    #     dist = idx / self.rate_ratio - math.floor(idx / self.rate_ratio)
    #
    #     if dist == 0:
    #         return source_frame
    #
    #     if not self.MV_field_idx < idx / self.rate_ratio < self.MV_field_idx + 1:
    #         target_frame = self.video_stream.get_frame(source_frame_idx + 1)
    #         # self.MV_field = get_motion_vectors(4, 10, source_frame, target_frame)
    #         self.MV_field_idx = source_frame_idx
    #
    #         self.MV_field = self.me_mode(self.blockSize, self.target_region, source_frame, target_frame)
    #         bwd = self.me_mode(self.blockSize, self.target_region, target_frame, source_frame)
    #         self.MV_field = smooth(self.smoothing_filter,self.MV_field,self.filterSize)
    #         bwd = smooth(self.smoothing_filter,bwd,self.filterSize)
    #
    #     Interpolated_Frame = np.ones(source_frame.shape, dtype='float64') * -1
    #     SAD_interpolated_frame = np.full([source_frame.shape[0], source_frame.shape[1]], np.inf)
    #
    #     for u in range(0, source_frame.shape[0]):
    #         for v in range(0, source_frame.shape[1]):
    #             if self.MV_field[u, v, 2] > bwd[u, v, 2]:
    #                 dist = 1.0 - dist
    #                 u_i = int(u + round(bwd[u, v, 0] * dist))
    #                 v_i = int(v + round(bwd[u, v, 1] * dist))
    #                 if(u_i<source_frame.shape[0] and v_i<source_frame.shape[1]):
    #
    #                     if bwd[u, v, 2] <= SAD_interpolated_frame[u_i, v_i]:
    #                         Interpolated_Frame[u_i, v_i] = target_frame[u, v]
    #                         SAD_interpolated_frame[u_i, v_i] = bwd[u, v, 2]
    #                         self.MV_field[u, v] = bwd[u, v]
    #
    #                     # self.MV_field[u,v,0] = bwd[u,v,0]
    #                     # self.MV_field[u,v,1] = bwd[u,v,1]
    #                     # self.MV_field[u,v,2] = bwd[u,v,2]
    #
    #             else:
    #                 u_i = int(u + round(self.MV_field[u, v, 0] * dist))
    #                 v_i = int(v + round(self.MV_field[u, v, 1] * dist))
    #                 if(u_i<source_frame.shape[0] and v_i<source_frame.shape[1]):
    #                     if self.MV_field[u, v, 2] <= SAD_interpolated_frame[u_i, v_i]:
    #                         Interpolated_Frame[u_i, v_i] = source_frame[u, v]
    #                         SAD_interpolated_frame[u_i, v_i] = self.MV_field[u, v, 2]
    #     k=10
    #     New_Interpolated_Frame = np.copy(Interpolated_Frame)
    #     for u in range(0, Interpolated_Frame.shape[0]):
    #         for v in range(0, Interpolated_Frame.shape[1]):
    #             if Interpolated_Frame[u,v,0] == -1:
    #                 u_min=max(0,u-k)
    #                 u_max=min(Interpolated_Frame.shape[0],u+k+1)
    #                 v_min=max(0,v-k)
    #                 v_max=min(Interpolated_Frame.shape[1],v+k+1)
    #                 New_Interpolated_Frame[u,v,0] = np.median(Interpolated_Frame[u_min:u_max,v_min:v_max,0])
    #                 New_Interpolated_Frame[u,v,1] = np.median(Interpolated_Frame[u_min:u_max,v_min:v_max,1])
    #                 New_Interpolated_Frame[u,v,2] = np.median(Interpolated_Frame[u_min:u_max,v_min:v_max,2])
    #
    #     New_Interpolated_Frame = New_Interpolated_Frame.astype(source_frame.dtype)
    #
    #     # print(self.filterSize,self.smoothing_filter,self.me_mode,self.target_region,self.blockSize)
    #     return New_Interpolated_Frame
    #
    # def __str__(self):
    #     return 'BI'


class BiDirInterpolator(BaseInterpolator):
    def __init__(self, target_fps,video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):

        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size)
        self.block_size = 8
        # print('sup bro set block_size here')
        # self.blockSize = block_size
        self.target_region = 7
        self.me_mode = ME_dict["HBMA"]
        # print(self.me_mode)
        self.filter_mode = smoothing_dict["weighted"]
        self.filterSize = 4
        self.sub_region = 1
        self.steps = 4
        self.min_block_size = 4

        print(args)
        if 'block_size' in args.keys():
            self.block_size = int(args['block_size'])
        if 'target_region' in args.keys():
            self.region = int(args['target_region'])
        if 'me_mode' in args.keys():
            self.me_mode = ME_dict[ args['me_mode']]
            if self.me_mode == tss:
                self.region = self.steps


    def get_interpolated_frame(self, idx):

        def gaussian_filter_2d(sigma):
            # sigma: the parameter sigma in the Gaussian kernel (unit: pixel)
            #
            # return: a 2D array for the Gaussian kernel
            def kernal(i,j):
                return 0.5/(math.pi*sigma*sigma) * np.exp(-(i*i+j*j)/(2*sigma*sigma))
            h =[]
            sample = np.arange(-4*sigma, 4*sigma+1)
            for x in sample:
                h.append([kernal(x,y) for y in sample])

            return h

        def convol(image):
            # first fill holes
            # second smooth it

            #h = gaussian_filter_2d(1)
            #h = [[1/9, 1/9,1/9],[1/9, 1/9,1/9],[1/9, 1/9,1/9]]
            #image[:,:,0] = scipy.signal.convolve2d(image[:,:,0], h ,mode='same', boundary='fill', fillvalue=0)
            #image[:,:,1] = scipy.signal.convolve2d(image[:,:,1], h ,mode='same', boundary='fill', fillvalue=0)
            #image[:,:,2] = scipy.signal.convolve2d(image[:,:,2], h ,mode='same', boundary='fill', fillvalue=0)

            h_sobel_x = [[1, 0,-1],[2,0,-2],[1,0,-1]]
            h_sobel_y = [[1,2,1],[0,0,0],[-1,-2,-1]]
            for i in range(3):
                x_axis = scipy.signal.convolve2d(image[:,:,i], h_sobel_x ,mode='same', boundary='fill', fillvalue=0)
                y_axis = scipy.signal.convolve2d(image[:,:,i], h_sobel_y ,mode='same', boundary='fill', fillvalue=0)
                # Calculate the gradient magnitude
                image[:,:,i] = np.sqrt(x_axis*x_axis+y_axis*y_axis)

            return image

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


        self.MV_field_idx= -1
        self.MV_field=[]
        source_frame_idx = math.floor(idx/self.rate_ratio)
        source_frame = self.video_stream.get_frame(source_frame_idx)
        dist = idx/self.rate_ratio - math.floor(idx/self.rate_ratio)

        if dist == 0:
            return source_frame
        if not self.MV_field_idx < idx/self.rate_ratio < self.MV_field_idx+1:
            target_frame = self.video_stream.get_frame(source_frame_idx+1)

            if(self.me_mode!=hbma):
                # self.me_mode = ME_dict[self.me_mode]
                self.MV_field= self.me_mode(self.block_size,self.target_region,source_frame,target_frame)
                bwd = self.me_mode(self.block_size, self.target_region, target_frame, source_frame)
            else:
                min_side = min(source_frame.shape[0],source_frame.shape[1])
                step_size=1
                while(min_side>255):
                    min_side/=2
                    step_size+=1
                self.steps=step_size
                self.MV_field= self.me_mode(self.block_size,self.target_region,self.sub_region,self.steps,self.min_block_size,source_frame,target_frame)
                bwd = self.me_mode(self.block_size,self.target_region,self.sub_region,self.steps,self.min_block_size,target_frame,source_frame)

            self.MV_field = smooth(self.filter_mode,self.MV_field,self.filterSize)
            self.MV_field_idx = source_frame_idx
            bwd = smooth(self.filter_mode,bwd,self.filterSize)

        Interpolated_Frame =  np.ones(source_frame.shape)*-1
        SAD_interpolated_frame = np.full([source_frame.shape[0],source_frame.shape[1]],np.inf)

        for u in range(0, source_frame.shape[0]):
            for v in range(0, source_frame.shape[1]):

                u_i = int(u + round(self.MV_field[u, v, 0] * dist))
                v_i = int(v + round(self.MV_field[u, v, 1] * dist))
                if(u_i<source_frame.shape[0] and v_i<source_frame.shape[1]):
                    if self.MV_field[u, v, 2] < SAD_interpolated_frame[u_i, v_i]:
                        Interpolated_Frame[u_i, v_i] = source_frame[u, v]
                        #Interpolated_Frame[u_i, v_i] = [0,0,source_frame[u, v ,2]]
                        SAD_interpolated_frame[u_i, v_i] = self.MV_field[u, v, 2]

                bwdist = 1.0 - dist
                u_i = int(u + round(bwd[u, v, 0] * bwdist))
                v_i = int(v + round(bwd[u, v, 1] * bwdist))
                if(u_i<source_frame.shape[0] and v_i<source_frame.shape[1]):
                    if bwd[u, v, 2] < SAD_interpolated_frame[u_i, v_i]:
                        if SAD_interpolated_frame[u_i, v_i] != np.inf :
                            t = bwd[u, v, 2]+SAD_interpolated_frame[u_i, v_i]
                            #Interpolated_Frame[u_i, v_i] = target_frame[u, v]*bwd[u, v, 2]/t + Interpolated_Frame[u_i, v_i]*SAD_interpolated_frame[u_i, v_i]/t
                            Interpolated_Frame[u_i, v_i] = target_frame[u, v]*SAD_interpolated_frame[u_i, v_i]/t + Interpolated_Frame[u_i, v_i]*bwd[u, v, 2]/t
                            SAD_interpolated_frame[u_i, v_i] = bwd[u, v, 2]
                        else:
                            Interpolated_Frame[u_i, v_i] = target_frame[u, v]
                            #Interpolated_Frame[u_i, v_i] = [0,target_frame[u, v ,1],0] #R G B
                            SAD_interpolated_frame[u_i, v_i] = bwd[u, v, 2]

        k=10

        New_Interpolated_Frame = np.copy(Interpolated_Frame)

        for u in range(0, Interpolated_Frame.shape[0]):
            for v in range(0, Interpolated_Frame.shape[1]):
                if Interpolated_Frame[u,v,0] == -1:
                    #to make sure the hole is not empty
                    Interpolated_Frame[u, v] = target_frame[u, v]
                    SAD_interpolated_frame[u, v] = self.MV_field[u, v, 2]

                    u_min=max(0,u-k)
                    u_max=min(Interpolated_Frame.shape[0],u+k+1)
                    v_min=max(0,v-k)
                    v_max=min(Interpolated_Frame.shape[1],v+k+1)
                    for i in range(3):
                        block = Interpolated_Frame[u_min:u_max,v_min:v_max,i]
                        block = block[block != -1]
                        New_Interpolated_Frame[u,v,i] = np.median(block)

        New_Interpolated_Frame = New_Interpolated_Frame.astype(source_frame.dtype)
        #New_Interpolated_Frame = Interpolated_Frame.astype(source_frame.dtype)
        #outframe = convol(New_Interpolated_Frame)
        return New_Interpolated_Frame

    def __str__(self):
        return 'bwMEMCI'

def MEMCI (target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
    mci_mode = 'unidir'

    if 'mci_mode' in args:
        mci_mode = args['mci_mode']

    if (mci_mode == 'unidir'):
        # print("unidir")
        # print(args['me_mode'])
        return UniDirInterpolator(target_fps, video_in_path, video_out_path, max_out_frames, max_cache_size,**args)
    elif (mci_mode == 'bidir'):
        # print("bidir")
        return BiDirInterpolator(target_fps, video_in_path, video_out_path, max_out_frames, max_cache_size,**args)
    elif (mci_mode == 'unidir2'):
        return UniDir2Interpolator(target_fps, video_in_path, video_out_path, max_out_frames, max_cache_size,**args)
    else:
        eprint(f'Unknown RRIN flow_usage_method argument: {mci_mode}')
        exit(1)

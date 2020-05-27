import imageio
import math
import time
import numpy as np
from io import BytesIO
from fractions import Fraction

import sys
sys.path.append('.')

from ..ME.full_search import get_motion_vectors as get_motion_vectors_fs
from ..ME.tss import get_motion_vectors as get_motion_vectors_tss
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
from .base import BaseInterpolator
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
    "full":get_motion_vectors_fs,
    "tss":get_motion_vectors_tss,
    "HBMA":hbma
}
smoothing_dict={
    "mean":mean_filter,
    "median":median_filter,
    "weighted":weighted_mean_filter

}
class MEMCIInterpolator(BaseInterpolator):
    def __init___(self, target_fps,video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):

        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size)


    def get_interpolated_frame(self, idx, block_size, target_region, ME_mode, filter_mode, filter_size):
        self.blockSize = block_size 
        self.target_region = target_region
        self.ME_method = ME_dict[ME_mode]
        self.smoothing_filter = smoothing_dict[filter_mode]
        self.filterSize = filter_size

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

    def get_interpolated_frame(self, idx,block_size, target_region, ME_mode, filter_mode, filter_size):
        self.blockSize = int(block_size) 
        self.target_region = int(target_region)
        self.ME_method = ME_dict[ME_mode]
        self.smoothing_filter = smoothing_dict[filter_mode]
        self.filterSize = int(filter_size)


        self.MV_field_idx= -1 #Index in source video that the current motion field is based on.
        self.MV_field=[]
        #for arg, value in args.items():
        #    setattr(self, arg, value)
        source_frame_idx = math.floor(idx / self.rate_ratio)
        source_frame = self.video_stream.get_frame(source_frame_idx)

        dist = idx / self.rate_ratio - math.floor(idx / self.rate_ratio)

        if dist == 0:
            return source_frame

        if not self.MV_field_idx < idx / self.rate_ratio < self.MV_field_idx + 1:
            target_frame = self.video_stream.get_frame(source_frame_idx + 1)
            # self.MV_field = get_motion_vectors(4, 10, source_frame, target_frame)
            self.MV_field_idx = source_frame_idx

            fwd = self.ME_method(self.blockSize, self.target_region, source_frame, target_frame)
            bwd = self.ME_method(self.blockSize, self.target_region, target_frame, source_frame)
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
                        Interpolated_Frame[u_i, v_i] = target_frame[u, v]
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


class bw(BaseInterpolator):
    def __init___(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size)


    def get_interpolated_frame(self, idx,**args):
        self.blockSize = 8 #args["blockSize"]
        self.target_region = 3 #args["target_region"]
        self.ME_method = ME_dict["tss"]#args["ME_method"]
        self.smoothing_filter = smoothing_dict["weighted"]#args["smoothing_filter"]#
        self.filterSize = 5 #args["filterSize"]

        self.MV_field_idx= -1 #Index in source video that the current motion field is based on.
        self.MV_field=[]

        for arg, value in args.items():
            setattr(self, arg, value)
        #source_frame is the previous frame in the source vidoe.
        source_frame_idx = math.floor(idx/self.rate_ratio)
        source_frame = self.video_stream.get_frame(source_frame_idx)

        #Normalized distance from current_frame to the source frame.
        dist = idx/self.rate_ratio - math.floor(idx/self.rate_ratio)

        #If the frame to be interpolated is coinciding with a source frame.
        if dist == 0:
            return source_frame


        #Check if the frame to be interpolated is between the two frames
        #that the current motion field is estimated on.
        if not self.MV_field_idx < idx/self.rate_ratio < self.MV_field_idx+1:
            target_frame = self.video_stream.get_frame(source_frame_idx+1)
            #self.MV_field = get_motion_vectors_fs(block_size, steps, source_frame, target_frame)
            self.MV_field = self.ME_method(self.blockSize, self.target_region, target_frame, source_frame)
            self.MV_field_idx = source_frame_idx


            #Uncomment if you want to plot vector field when running benchmark.py
            #self.plot_vector_field(block_size,steps, source_frame)




        #Initialize new frame
        Interpolated_Frame =  np.ones(source_frame.shape)*-1
        #Matrix with lowest sad value fo every interpolated pixel.
        SAD_interpolated_frame = np.full([source_frame.shape[0],source_frame.shape[1]],np.inf)

        #Follow motion vectorcs to obtain interpolated pixel Values
        #If interpolated frame has multiple values, take the one with lowest SAD.
        for u in range(0, target_frame.shape[0]):
            for v in range(0, target_frame.shape[1]):

                #Get the new coordinates by following scaled MV.
                u_i = int(u + round(self.MV_field[u,v,0]*dist))
                v_i = int(v + round(self.MV_field[u,v,1]*dist))

                if  self.MV_field[u,v,2] <= SAD_interpolated_frame[u_i, v_i]:

                    Interpolated_Frame[u_i, v_i] =  target_frame[u, v]
                    SAD_interpolated_frame[u_i, v_i] = self.MV_field[u,v,2]



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
        return New_Interpolated_Frame


    def plot_vector_field(self,block_size,steps,source_frame):
        #Downsample so each vector represents one block.

        Down_sampled_MV=self.MV_field[::block_size,::block_size,:]
        X, Y = np.meshgrid(np.linspace(0,self.MV_field.shape[1]-1, Down_sampled_MV.shape[1]), \
                            np.linspace(0,self.MV_field.shape[0]-1, Down_sampled_MV.shape[0]))

        U = Down_sampled_MV[:,:,0]  #X-direction
        V = Down_sampled_MV[:,:,1]  #Y-direction
        M = np.hypot(U, V)          #Magnitude of vector.

        fig, ax = plt.subplots(1,1)
        source_image = ax.imshow(source_frame)
        vector_field = ax.quiver(X, Y, U, V ,M,cmap='coolwarm', angles='uv',units='x', pivot='tip', width=1,
                       scale=1 / 0.5)

        cbar=fig.colorbar(vector_field)
        cbar.ax.set_ylabel('|MV| in pixels')
        plt.title("Block size="+str(block_size)+ "\nSteps="+str(steps))
        plt.show()

    def __str__(self):
        return 'bwMEMCI'
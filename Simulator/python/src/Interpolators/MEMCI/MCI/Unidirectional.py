import imageio
import math
import time
import numpy as np

from ..ME.hbma import get_motion_vectors as hbma
from ..smoothing.threeXthree_mv_smoothing import smooth
from ....util import get_first_frame_idx_and_ratio


from .MEMCIBaseInterpolator import MEMCIBaseInterpolator

'''
MEMCI using full search for ME and uniderictional
MCI with median filter for filling holes.



'''
class UniDirInterpolator(MEMCIBaseInterpolator):
    def __init__(self, target_fps,video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size,**args)

    ### this function should be only self, idx, like in BaseInterpolator
    def get_interpolated_frame(self, idx):
        # self.MV_field_idx= -1 #Index in source video that the current motion field is based on.
        # self.MV_field=[]

        #source_frame is the previous frame in the source vidoe.
        source_frame_idx, inv_dist = get_first_frame_idx_and_ratio(idx, self.rate_ratio)

        dist = 1. - inv_dist

        source_frame = self.video_stream.get_frame(source_frame_idx)
        #If the frame to be interpolated is coinciding with a source frame.
        if math.isclose(dist,0.):
            return source_frame

        #Check if the frame to be interpolated is between the two frames
        #that the current motion field is estimated on.
        if not self.MV_field_idx < idx/self.rate_ratio < self.MV_field_idx+1:
            target_frame = self.video_stream.get_frame(source_frame_idx+1)
            # print(self.me_mode)
            if(self.me_mode!=hbma):

                # self.me_mode = ME_dict[self.me_mode]
                self.MV_field= self.me_mode(self.block_size,self.region,source_frame,target_frame)
            else:
                min_side = min(source_frame.shape[0],source_frame.shape[1])
                step_size=1
                while(min_side>255):
                    min_side/=2
                    step_size+=1
                self.steps=step_size
                self.MV_field= self.me_mode(self.block_size,self.region,self.sub_region,self.steps,self.min_block_size,source_frame,target_frame)

            self.MV_field = smooth(self.filter_mode,self.MV_field,self.filterSize)
            self.MV_field_idx = source_frame_idx


            #Uncomment if you want to plot vector field when running benchmark.py
            #self.plot_vector_field(block_size,steps, source_frame)




        #Initialize new frame
        Interpolated_Frame =  np.full(source_frame.shape, -1) 
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

        # print(self.filterSize,self.smoothing_filter,self.me_mode,self.target_region,self.blockSize)
        return New_Interpolated_Frame
    def __str__(self):
        return 'uniMEMCI'




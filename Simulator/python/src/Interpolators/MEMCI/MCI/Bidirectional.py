
from .MEMCIBaseInterpolator import MEMCIBaseInterpolator
import math
import numpy as np
import scipy
from ..smoothing.threeXthree_mv_smoothing import smooth
from ..ME.hbma import get_motion_vectors as hbma

class BiDirInterpolator(MEMCIBaseInterpolator):
    def __init__(self, target_fps,video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):

        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size,**args)


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


        # self.MV_field_idx= -1
        # self.MV_field=[]
        source_frame_idx = math.floor(idx/self.rate_ratio)
        source_frame = self.video_stream.get_frame(source_frame_idx)
        dist = idx/self.rate_ratio - math.floor(idx/self.rate_ratio)

        if dist == 0:
            return source_frame
        if not self.MV_field_idx < idx/self.rate_ratio < self.MV_field_idx+1:
            target_frame = self.video_stream.get_frame(source_frame_idx+1)

            if(self.me_mode!=hbma):
                # self.me_mode = ME_dict[self.me_mode]
                self.MV_field= self.me_mode(self.block_size,self.region,source_frame,target_frame)
                bwd = self.me_mode(self.block_size, self.region, target_frame, source_frame)
            else:
                min_side = min(source_frame.shape[0],source_frame.shape[1])
                step_size=1
                while(min_side>255):
                    min_side/=2
                    step_size+=1
                self.steps=step_size
                self.MV_field= self.me_mode(self.block_size,self.region,self.sub_region,self.steps,self.min_block_size,source_frame,target_frame)
                bwd = self.me_mode(self.block_size,self.region,self.sub_region,self.steps,self.min_block_size,target_frame,source_frame)

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
import imageio
import math
import time
import numpy as np
from io import BytesIO
from scipy import signal
from fractions import Fraction
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


def gkern(kernlen=8, std=0.5):
#Returns a 2D Gaussian kernel of size (kernlen x kernlen) array.
    gkern1d = signal.gaussian(kernlen, std=std).reshape(kernlen, 1)
    gkern2d = np.outer(gkern1d, gkern1d)
    return gkern2d*15


class Uni_2(BaseInterpolator):
    def __init___(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):

        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size)


    def get_interpolated_frame(self, idx):

        #source_frame is the previous frame in the source vidoe.
        source_frame_idx = math.floor(idx/self.rate_ratio)
        source_frame = self.video_stream.get_frame(source_frame_idx)

        #Normalized distance from current_frame to the source frame.
        dist = idx/self.rate_ratio - math.floor(idx/self.rate_ratio)

        #If the frame to be interpolated is coinciding with a source frame.
        if dist == 0:
            return source_frame

        target_frame = self.video_stream.get_frame(source_frame_idx+1)


        #Check if the frame to be interpolated is between the two frames
        #that the current motion field is estimated on.
        if not self.MV_field_idx < idx/self.rate_ratio < self.MV_field_idx+1:
            self.MV_field_idx = source_frame_idx
            block_size = 16
            region = 15
            sub_region = 1
            steps = 1
            min_block_size = 4
            self.fwr_MV_field = hbma(block_size,
                                region,
                                sub_region,
                                steps,
                                min_block_size,
                                source_frame, target_frame)
            '''self.bwr_MV_field = hbma(block_size,
                                region,
                                sub_region,
                                steps,
                                min_block_size,
                                target_frame, source_frame)'''

        #Uncomment if you want to plot vector field when running benchmark.py
        self.MV_field = self.fwr_MV_field
        self.plot_vector_field(min_block_size,steps, source_frame)

        Intrpol_fwr = self.IEWMC(source_frame,target_frame,dist)
        Intrpol_bwr = self.IEWMC(target_frame,source_frame,1-dist)

        Intepol_comb = self.Error_adaptive_combination(Intrpol_fwr, Intrpol_bwr)

        Intrpol_frame = self.BDHI(Intepol_comb)

        return Intrpol_frame





    #Irregular-Grid Expanded-Block
    #Weighted Motion-Compensation
    def IEWMC(self,F1,F2,dist):
        ##Initialization##
        #accumulations of the weighted motion compensations
        accumulations = np.zeros(F1.shape)
        #weights
        weights = np.zeros(F1.shape)
        #weighted motion compensation differences.
        WMCD = np.zeros(F1.shape)


        w = gkern(8,1.8)
        ##Accumulations##


        #Normalization

        return None

    #Error-Adaptive Combination
    def Error_adaptive_combination(self, Ff, Fb):
        print('hej')

    #Block-Wise Directional Hole Interpolation
    def BDHI(self,Fc):
        print('hej')



    def plot_vector_field(self,block_size,steps,source_frame):
        #Downsample so each vector represents one block.


        Down_sampled_MV=self.MV_field[::block_size,::block_size,:]
        X, Y = np.meshgrid(np.linspace(0,self.MV_field.shape[1]-1, Down_sampled_MV.shape[1]), \
                            np.linspace(0,self.MV_field.shape[0]-1, Down_sampled_MV.shape[0]))

        U = Down_sampled_MV[:,:,0]*-1

        V = Down_sampled_MV[:,:,1]
        M = np.hypot(U, V)          #Magnitude of vector.
        print(self.MV_field.shape)
        fig, ax = plt.subplots(1,1)
        source_image = ax.imshow(source_frame)
        vector_field = ax.quiver(X, Y, V, U ,M,cmap='coolwarm', angles='uv',units='x', pivot='tip', width=1,
                       scale=1 / 0.5)

        cbar=fig.colorbar(vector_field)
        cbar.ax.set_ylabel('|MV| in pixels')
        plt.title("Block size="+str(block_size)+ "\nSteps="+str(steps))
        plt.show()

    def __str__(self):
        return 'Uni_2'

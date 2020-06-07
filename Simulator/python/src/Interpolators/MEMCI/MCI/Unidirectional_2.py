import imageio
import math
import time
import numpy as np
from io import BytesIO
from scipy import signal
from fractions import Fraction
from ..ME.full_search import get_motion_vectors as full
from ..ME.tss import get_motion_vectors as tss
from ..ME.hbma import get_motion_vectors as hbma
from decimal import Decimal
from copy import deepcopy
# from Globals import debug_flags
# from VideoStream import BenchmarkVideoStream, VideoStream
import matplotlib.pyplot as plt
from ..smoothing.threeXthree_mv_smoothing import smooth
from ..smoothing.median_filter import median_filter
from ..smoothing.mean_filter import mean_filter
from ..smoothing.weighted_mean_filter import weighted_mean_filter

from ...base import BaseInterpolator

'''
This motion compensated frame interpolation (MCFI) method
is based on the algorithm presented by
D. Wang, A. Vincent, P Blanchfield, and R Klepko in
"Motion-Compensated Frame Rate Up-Conversion—Part II: New
Algorithms for Frame Interpolation".
Link: https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=5440975
'''

ME_dict={
    "full":full,
    "tss":tss,
    "hbma":hbma,
}

def get_weight_kern(kernlen=8):
#Returns a 3D  kernel of size (kernlen x kernlen x 3).
    x = np.linspace(1,1.1,int(kernlen/2))
    x = np.append(x, np.flip(x))
    xx, yy = np.meshgrid(x,x)
    weights = 6*np.square(5*(np.log2(xx)+np.log2(yy)))
    '''weights = np.array([[0,1,1,2,2,1,1,0],
                        [1,2,4,5,5,4,2,1],
                        [1,4,6,9,9,6,4,1],
                        [2,5,9,12,12,9,5,2],
                        [2,5,9,12,12,9,5,2],
                        [1,4,6,9,9,6,4,1],
                        [1,2,4,5,5,4,2,1],
                        [0,1,1,2,2,1,1,0]])'''
    weights = np.repeat(weights[:, :, np.newaxis], 3, axis=2)

    return weights


class UniDir2Interpolator(BaseInterpolator):
    def __init__(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):

        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size)
        self.MV_field_idx = -1
        self.fwr_MV_field = []
        self.bwr_MV_field = []
        self.large_block_size = 8
        self.region = 7
        self.me_mode = ME_dict["HBMA"]
        self.sub_region = 1
        self.steps = 1
        self.block_size = 4
        self.upscale_MV = True
        if 'block_size' in args.keys():
            self.large_block_size = int(args['block_size'])
        if 'target_region' in args.keys():
            self.region = int(args['target_region'])
        if 'me_mode' in args.keys():
            self.me_mode = ME_dict[ args['me_mode']]

        self.pad_size = 4*self.block_size

        if self.me_mode == full:
            self.ME_args = {"block_size":self.large_block_size, "target_region":self.region}

        elif self.me_mode == tss:
            self.ME_args = {"block_size":self.large_block_size, "steps":self.steps}

        elif self.me_mode == hbma:

            self.upscale_MV = False
            self.ME_args = {"block_size":self.large_block_size,"win_size":self.region,
                            "sub_win_size":self.sub_region, "steps":self.steps,
                            "min_block_size":self.block_size,
                            "cost":"sad", "upscale":self.upscale_MV}

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
            if self.me_mode==hbma:
                min_side = min(source_frame.shape[0], source_frame.shape[1])
                step_size = 1
                while (min_side > 255):
                    min_side /= 2
                    step_size += 1
                self.ME_args["steps"] = step_size
            self.fwr_MV_field = self.me_mode(**self.ME_args, im1=source_frame, im2=target_frame)
            self.bwr_MV_field = self.me_mode(**self.ME_args, im1=target_frame, im2=source_frame)

        #Uncomment if you want to plot vector field when running benchmark.py
        self.MV_field = self.fwr_MV_field
        # self.plot_vector_field(source_frame)

        #Get forward and backward intermidiate

        Ff, Ef = self.IEWMC(self.fwr_MV_field, source_frame, target_frame, dist)
        Fb, Eb = self.IEWMC(self.bwr_MV_field, target_frame, source_frame, 1-dist)

        #Get combined frame
        Fc = self.Error_adaptive_combination(Ff, Ef, Fb, Eb)

        #Fill holes in the combined frame
        Fc_filled = self.BDHI(Fc)

        # self.show_images(Ff,Fb,Fc,Fc_filled)


        #Remove padding
        Out_frame = Fc_filled[self.pad_size:-self.pad_size,self.pad_size:-self.pad_size,:]

        return Out_frame.astype(source_frame.dtype)


    #Irregular-Grid Expanded-Block
    #Weighted Motion-Compensation
    def IEWMC(self, MV_field, F1, F2, dist):
        frame_shape = F1.shape
        thresh = 250 # SAD threshold to determine occluded blocks.

        ##Initialization##
        #Pad input images to deal with expanded blocks.
        F1 = np.pad(F1, ((self.pad_size,self.pad_size), (self.pad_size,self.pad_size), (0,0)))  # to allow for non divisible block sizes
        F2 = np.pad(F2, ((self.pad_size,self.pad_size), (self.pad_size,self.pad_size), (0,0)))

        #accumulations of the weighted motion compensations
        accumulations = np.zeros(F1.shape)
        #Saved weights
        weights = np.zeros(F1.shape)
        #weighted motion compensation differences.
        WMCD = np.zeros(F1.shape)




        #Weights
        w = get_weight_kern(2*self.block_size)
        SAD_norm = self.block_size*self.block_size*3
        #Iterate trough all blocks.
        ##Accumulations##

        for block_row_index in range(0, frame_shape[0], self.block_size):
            for block_col_index in range(0, frame_shape[1], self.block_size):


                if self.upscale_MV == False:
                    MV_i = MV_field[int(block_row_index/self.block_size), int(block_col_index/self.block_size), 0:3]

                else:
                    MV_i = MV_field[block_row_index, block_col_index, 0:3]
                Xb = int(MV_i[0])  #Scaled motion vector within current block.
                Yb = int(MV_i[1])
                TXb = int(dist*Xb)
                TYb = int(dist*Yb)
                SAD = MV_i[2]/SAD_norm

                i = block_row_index + self.pad_size
                j = block_col_index + self.pad_size

                SAD = MV_field[block_row_index, block_col_index,2]/SAD_norm

                #Index for expanded block.
                min_row = i-(int(self.block_size/2))
                max_row = i+self.block_size+(int(self.block_size/2))
                min_col = j-(int(self.block_size/2))
                max_col = j+self.block_size+(int(self.block_size/2))



                if SAD < thresh:
                    acc = np.multiply(w,(((1-dist)*(F1[min_row:max_row,min_col:max_col,:]))+(dist*F2[min_row+Xb:max_row+Xb,min_col+Yb:max_col+Yb,:])))
                else:
                    acc = np.multiply(w,F1[min_row:max_row,min_col:max_col,:])
                accumulations[min_row+Xb:max_row+Xb,min_col+Yb:max_col+Yb,:]+= acc

                WM = np.multiply(w,np.absolute(F1[min_row:max_row,min_col:max_col,:]-F2[min_row+Xb:max_row+Xb,min_col+Yb:max_col+Yb,:]))
                WMCD[min_row+Xb:max_row+Xb,min_col+Yb:max_col+Yb,:] += WM

                weights[min_row+Xb:max_row+Xb,min_col+Yb:max_col+Yb,:] += w

        F = np.zeros(F1.shape)    #interpolated frame
        E = np.zeros(F2.shape)    #weighted average

        ##Normalization##
        for row in range(0,accumulations.shape[0]):
            for col in range(0,accumulations.shape[1]):
                if weights[row,col,0] <= 0:
                    F[row,col,:] = -1
                    E[row,col,:] = -1
                else:
                    F[row,col,:] = accumulations[row,col,:]/weights[row,col,0]
                    E[row,col,:] = WMCD[row,col,:]/weights[row,col,0]


        return F, E


    #Error-Adaptive Combination
    def Error_adaptive_combination(self, Ff, Ef, Fb, Eb):
        Fc = np.full(Ff.shape,-1)

        alpha = 8 #Empirically determined parameter used to smooth the weights.

        for i in range(0,Ff.shape[0]):
            for j in range(0,Ff.shape[1]):

                if (Ff[i,j,0] != -1) and (Fb[i,j,0] != -1):
                    Fc[i,j,:] = (((Eb[i,j,:]+alpha)*(Ff[i,j,:]))+((Ef[i,j,:]+alpha)*(Fb[i,j,:])))/(Ef[i,j,:]+Eb[i,j,:]+(2*alpha))

                elif Ff[i,j,0] != -1:
                    Fc[i,j,:] = Ff[i,j,:]

                elif Fb[i,j,0] != -1 :
                    Fc[i,j,:] = Fb[i,j,:]

        return Fc

    #Block-Wise Directional Hole Interpolation
    def BDHI(self,Fc):
        Fc_out = np.copy(Fc)
        fill_block_size = 2*self.block_size
        for row_index in range(self.pad_size,Fc.shape[0]-self.pad_size, fill_block_size):
            for col_index in range(self.pad_size, Fc.shape[1]-self.pad_size, fill_block_size):
                block = Fc[row_index:row_index+(fill_block_size),col_index:col_index+fill_block_size,:]

                if -1 in block[:,:,0]:
                    filled_block = self.fill_holes(block)
                    Fc_out[row_index:row_index+fill_block_size,col_index:col_index+fill_block_size,:] = filled_block

        return Fc_out

    def fill_holes(self,block):
        block_out = np.copy(block)
        ah = np.array([0.1,0.1,0.1,0.1]) #Average Abs differences in each direction.
        av = np.array([0.1,0.1,0.1,0.1])
        ad = np.array([0.1,0.1,0.1,0.1])
        ar = np.array([0.1,0.1,0.1,0.1])
        #Calculate absolute differences between adjacent interpolated pixels
        # in each direction.
        for i in range(0,block.shape[0]-1):
            for j in range(0,block.shape[1]-1):
                if block[i,j,0] != -1:
                    pi = block[i,j,:]

                    if block[i+1,j,0] != -1:
                        ah[0:3] += np.absolute(pi-block[i+1,j,:])
                        ah[3]+= 1

                    if block[i,j+1,0] != -1:
                        av[0:3] += np.absolute(pi-block[i,j+1,:])
                        av[3]+= 1

                    if block[i+1,j+1,0] != -1:
                        ad[0:3] += np.absolute(pi-block[i+1,j+1,:])
                        ad[3]+= 1

                    if (block[i-1,j+1,0] != -1) and (i-1>-1):
                        ar[0:3] += np.absolute(pi-block[i-1,j+1,:])
        ah = ah[0:3]/ah[3]
        av = av[0:3]/av[3]
        ad = ad[0:3]/ad[3]
        ar = ar[0:3]/ar[3]

        a_array = np.array([ah,av,ad,ar])

        #For undetermined pixel within the block,
        #performe linear interpolation in each direction.
        p_directions = np.array([[1,0],[0,1],[1,1],[-1,1]])
        for i in range(0,block.shape[0]):
            for j in range(0,block.shape[1]):
                if block[i,j,0] == -1:
                    p_array = np.full((4,3),-1)

                    for p_index in range(0,p_directions.shape[0]):
                        p = p_directions[p_index,:]

                        n1 = i
                        n2 = i
                        m1 = j
                        m2 = j
                        p1 = np.full(block[i,j,:].shape,-1)
                        p2 = np.full(block[i,j,:].shape,-1)

                        while (p1[0] == -1) and ( 0<= n1 < block.shape[0]) and (0 <= m1 < block.shape[1]):

                            if block[n1,m1,0] != -1:
                                p1 = block[n1,m1,:]
                                d1 = np.hypot(i-n1,j-m1)

                            n1 -= p[0]
                            m1 -= p[1]
                        while (p2[0] == -1) and ( 0<= n2< block.shape[0]) and (0 <= m2 < block.shape[1]):

                            if block[n2,m2,0] != -1:
                                p2 = block[n2,m2,:]
                                d2 = np.hypot(i-n2,j-m2)
                            n2 += p[0]
                            m2 += p[1]
                        if (p1[0] != -1) and (p2[0] != -1):
                            p_array[p_index,:] =((d2*p1)+(d1*p2))/(d1+d2)

                        elif p1[0] != -1:
                            p_array[p_index,:] = p1


                        elif p2[0] != -1 :
                            p_array[p_index,:] = p2
                    A = 0
                    pixel_interp = 0

                    for direction in range(0,a_array.shape[0]):
                        if p_array[direction,0] != -1:
                            A+= 1/a_array[direction,:]

                            pixel_interp+= p_array[direction,:]/a_array[direction,:]

                    if isinstance(A, np.ndarray):
                        pixel_interp = pixel_interp/A
                        block_out[i,j,:] = pixel_interp

        return block_out

    def plot_vector_field(self,source_frame):
        #Downsample so each vector represents one block.
        if self.upscale_MV == False:
            Down_sampled_MV = self.MV_field
            X, Y = np.meshgrid(np.linspace(0,(self.MV_field.shape[1]*self.block_size)-1, Down_sampled_MV.shape[1]), \
                                np.linspace(0,(self.MV_field.shape[0]*self.block_size) -1, Down_sampled_MV.shape[0]))
        else :
            Down_sampled_MV=self.MV_field[::self.block_size,::self.block_size,:]
            X, Y = np.meshgrid(np.linspace(0,self.MV_field.shape[1]-1, Down_sampled_MV.shape[1]), \
                                np.linspace(0,self.MV_field.shape[0]-1, Down_sampled_MV.shape[0]))

        U = Down_sampled_MV[:,:,0]*-1
        V = Down_sampled_MV[:,:,1]

        M = np.hypot(U, V)          #Magnitude of vector.
        fig, ax = plt.subplots(1,1)
        source_image = ax.imshow(source_frame)
        vector_field = ax.quiver(X, Y, V, U ,Down_sampled_MV[:,:,2],cmap='coolwarm', angles='uv',units='x', pivot='tip', width=1,
                       scale=1 / 0.5)

        cbar=fig.colorbar(vector_field)
        cbar.ax.set_ylabel('|MV| in pixels')
        plt.title("Block size="+str(self.block_size)+ "\nSteps="+str(self.steps))
        plt.show()

    def show_images(self, Ff, Fb, Fc, Fc_filled):

        f, ax = plt.subplots(2,2,sharex=True, sharey=True)
        ax[0][0].imshow(Ff.astype(int))
        ax[0][0].set_title('Forward intermediate frame')

        ax[0][1].imshow(Fb.astype(int))
        ax[0][1].set_title('Backward intermediate frame')

        ax[1][0].imshow(Fc.astype(int))
        ax[1][0].set_title('Combined frame')

        ax[1][1].imshow(Fc_filled.astype(int))
        ax[1][1].set_title('Combined frame with filled holes.')
        plt.show()

    def __str__(self):
        return 'Uni_2'

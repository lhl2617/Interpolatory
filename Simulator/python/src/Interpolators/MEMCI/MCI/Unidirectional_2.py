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
from ....util import get_first_frame_idx_and_ratio
# from Globals import debug_flags
# from VideoStream import BenchmarkVideoStream, VideoStream
from numba import njit, types, uint8, int32, float32, boolean, float64, int64
from ...base import BaseInterpolator
from .MEMCIBaseInterpolator import MEMCIBaseInterpolator
from ..smoothing.threeXthree_mv_smoothing import smooth

'''
This motion compensated frame interpolation (MCFI) method
is based on the algorithm presented by
D. Wang, A. Vincent, P Blanchfield, and R Klepko in
"Motion-Compensated Frame Rate Up-Conversion—Part II: New
Algorithms for Frame Interpolation".
Link: https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=5440975
'''

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
    weights = np.repeat(weights[:, :, np.newaxis], 3, axis=2).astype(np.float32)

    return weights


@njit(types.UniTuple(float32[:,:,:], 2)(types.UniTuple(int32, 3), uint8[:,:,:], uint8[:,:,:], int32, float32[:,:,:], boolean, int32, float32, float32[:,:,:]), cache=True)
def IEWMC_helper(frame_shape, F1_pad, F2_pad, min_block_size, MV_field, upscale_MV, pad_size, dist, w):
    #accumulations of the weighted motion compensations
    accumulations = np.zeros(F1_pad.shape, dtype=np.float32)
    #Saved weights
    weights = np.zeros(F1_pad.shape, dtype=np.float32)
    #weighted motion compensation differences.
    WMCD = np.zeros(F1_pad.shape, dtype=np.float32)
    thresh = 250 # SAD threshold to determine occluded blocks.

    SAD_norm = min_block_size*min_block_size*3

    for block_row_index in range(0, frame_shape[0], min_block_size):
        for block_col_index in range(0, frame_shape[1], min_block_size):
            if upscale_MV == False:
                MV_i = MV_field[int(block_row_index/min_block_size), int(block_col_index/min_block_size), 0:3]

            else:
                MV_i = MV_field[block_row_index, block_col_index, 0:3]
            Xb = int(MV_i[0])  #Scaled motion vector within current block.
            Yb = int(MV_i[1])
            TXb = int(dist*Xb)
            TYb = int(dist*Yb)
            SAD = MV_i[2]/SAD_norm

            i = block_row_index + pad_size
            j = block_col_index + pad_size

            #Index for expanded block.
            min_row = i-(int(min_block_size/2))
            max_row = i+min_block_size+(int(min_block_size/2))
            min_col = j-(int(min_block_size/2))
            max_col = j+min_block_size+(int(min_block_size/2))

            acc = np.zeros((max_row-min_row, max_col-min_col, 3), dtype=np.float32)

            if SAD < thresh:
                t_1 = F1_pad[min_row:max_row,min_col:max_col,:]
                t_a = (1-dist) * t_1

                t_2 = F2_pad[min_row+Xb:max_row+Xb,min_col+Yb:max_col+Yb,:]
                t_b = dist * t_2

                t_c = t_a + t_b

                acc += np.multiply(w, t_c)
            else:
                acc += np.multiply(w,F1_pad[min_row:max_row,min_col:max_col,:])

            accumulations[min_row+TXb:max_row+TXb,min_col+TYb:max_col+TYb,:] += acc

            F1_portion = F1_pad[min_row:max_row,min_col:max_col,:].astype(np.int32)
            F2_portion = F2_pad[min_row+Xb:max_row+Xb,min_col+Yb:max_col+Yb,:].astype(np.int32)

            WM = np.multiply(w, np.absolute(F1_portion - F2_portion)).astype(np.float32)
            WMCD[min_row+TXb:max_row+TXb,min_col+TYb:max_col+TYb,:] += WM

            weights[min_row+TXb:max_row+TXb,min_col+TYb:max_col+TYb,:] += w

    F = np.zeros(F1_pad.shape, dtype=np.float32)    #interpolated frame
    E = np.zeros(F2_pad.shape, dtype=np.float32)    #weighted average

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

#Irregular-Grid Expanded-Block
#Weighted Motion-Compensation
def IEWMC(MV_field, F1, F2, dist, pad_size, min_block_size, upscale_MV):
    frame_shape = F1.shape

    ##Initialization##
    #Pad input images to deal with expanded blocks.
    F1_pad = np.pad(F1, ((pad_size,pad_size), (pad_size,pad_size), (0,0)))  # to allow for non divisible block sizes
    F2_pad = np.pad(F2, ((pad_size,pad_size), (pad_size,pad_size), (0,0)))

    #Weights
    w = get_weight_kern(2*min_block_size)
    #Iterate trough all blocks.
    ##Accumulations##

    return IEWMC_helper(frame_shape, F1_pad, F2_pad, min_block_size, MV_field, upscale_MV, pad_size, dist, w)


#Error-Adaptive Combination
@njit(float32[:,:,:](float32[:,:,:],float32[:,:,:],float32[:,:,:],float32[:,:,:]), cache=True)
def Error_adaptive_combination(Ff, Ef, Fb, Eb):
    Fc = np.full(Ff.shape, -1, dtype=np.float32)

    alpha = 1 #Empirically determined parameter used to smooth the weights.

    for i in range(0,Ff.shape[0]):
        for j in range(0,Ff.shape[1]):

            if (Ff[i,j,0] != -1) and (Fb[i,j,0] != -1):
                Fc[i,j,:] = (((Eb[i,j,:]+alpha)*(Ff[i,j,:]))+((Ef[i,j,:]+alpha)*(Fb[i,j,:])))/(Ef[i,j,:]+Eb[i,j,:]+(2*alpha))

            elif Ff[i,j,0] != -1:
                Fc[i,j,:] = Ff[i,j,:]

            elif Fb[i,j,0] != -1 :
                Fc[i,j,:] = Fb[i,j,:]

    return Fc

@njit(float32[:,:,:](float32[:,:,:]), cache=True)
def fill_holes(block):
    block_out = np.copy(block)
    ah = np.array([0.1,0.1,0.1,0.1], dtype=np.float32) #Average Abs differences in each direction.
    av = np.array([0.1,0.1,0.1,0.1], dtype=np.float32) 
    ad = np.array([0.1,0.1,0.1,0.1], dtype=np.float32) 
    ar = np.array([0.1,0.1,0.1,0.1], dtype=np.float32) 
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

    a_array = np.empty((4, 3), dtype=np.float32)
    a_array[0] = ah
    a_array[1] = av
    a_array[2] = ad
    a_array[3] = ar

    #For undetermined pixel within the block,
    #performe linear interpolation in each direction.
    p_directions = np.array([[1,0],[0,1],[1,1],[-1,1]], dtype=np.float32)
    for i in range(block.shape[0]):
        for j in range(block.shape[1]):
            if block[i,j,0] == -1:
                p_array = np.full((4,3),-1)

                for p_index in range(p_directions.shape[0]):
                    p = p_directions[p_index,:]

                    n1 = i
                    n2 = i
                    m1 = j
                    m2 = j
                    p1 = np.full(block[i,j,:].shape,-1, dtype=np.float32)
                    p2 = np.full(block[i,j,:].shape,-1, dtype=np.float32)


                    while (-1 == p1[0]) and (0 <= n1 < block.shape[0]) and (0 <= m1 < block.shape[1]):
                        # the cast is because in n1 -= p[0] n1 is promoted to float...
                        if -1 != block[int(n1),int(m1),0]:
                            p1 = block[int(n1),int(m1),:]
                            d1 = np.hypot(i-n1,j-m1)

                        n1 -= p[0]
                        m1 -= p[1]

                    while (-1 == p2[0]) and (0 <= n2 < block.shape[0]) and (0 <= m2 < block.shape[1]):
                        if block[int(n2),int(m2),0] != -1:
                            p2 = block[int(n2),int(m2),:]
                            d2 = np.hypot(i-n2,j-m2)
                        n2 += p[0]
                        m2 += p[1]

                    if (p1[0] != -1) and (p2[0] != -1):
                        p_array[p_index,:] =((d2*p1)+(d1*p2))/(d1+d2)

                    elif p1[0] != -1:
                        p_array[p_index,:] = p1


                    elif p2[0] != -1 :
                        p_array[p_index,:] = p2

                A = np.zeros(ah.shape, dtype=np.float32)
                pixel_interp = np.zeros(ah.shape, dtype=np.float32)

                for direction in range(4):
                    if p_array[direction,0] != -1:
                        A += 1 / a_array[direction,:]
                        pixel_interp+= p_array[direction,:] / a_array[direction,:]

                # if isinstance(A, np.ndarray):
                pixel_interp = pixel_interp / A
                block_out[i,j,:] = pixel_interp

    return block_out


#Block-Wise Directional Hole Interpolation
@njit(float32[:,:,:](float32[:,:,:], int32, int32), cache=True)
def BDHI(Fc, min_block_size, pad_size):
    Fc_out = np.copy(Fc)
    fill_block_size = 2*min_block_size
    for row_index in range(pad_size,Fc.shape[0]-pad_size, fill_block_size):
        for col_index in range(pad_size, Fc.shape[1]-pad_size, fill_block_size):
            block = Fc[row_index:row_index+(fill_block_size),col_index:col_index+fill_block_size,:]

            contains_neg_1 = False

            # numba limitation, can't support in
            for b in block[:,:,0]:
                for c in b:
                    if c == -1:
                        contains_neg_1 = True
                        break
                if contains_neg_1:
                    break

            if contains_neg_1:
                filled_block = fill_holes(block)
                Fc_out[row_index:row_index+fill_block_size,col_index:col_index+fill_block_size,:] = filled_block

    return Fc_out

@njit(uint8[:,:,:](float32[:,:,:], int32), cache=True)
def unpad_and_downconvert(frame, pad_size):
    return frame[pad_size:-pad_size,pad_size:-pad_size,:].astype(np.uint8)

class UniDir2Interpolator(MEMCIBaseInterpolator):
    def __init__(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):

        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size,**args)

    def get_interpolated_frame(self, idx):
        source_frame_idx, inv_dist = get_first_frame_idx_and_ratio(idx, self.rate_ratio)

        dist = 1. - inv_dist

        source_frame = self.video_stream.get_frame(source_frame_idx)
        #If the frame to be interpolated is coinciding with a source frame.
        if math.isclose(dist,0.):
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
                # print(self.ME_args)
            self.fwr_MV_field = self.me_mode(**self.ME_args, im1=source_frame, im2=target_frame)
            self.bwr_MV_field = self.me_mode(**self.ME_args, im1=target_frame, im2=source_frame)
        #Uncomment if you want to plot vector field when running benchmark.py
        self.MV_field = self.fwr_MV_field
        #self.plot_vector_field(source_frame)

        #Get forward and backward intermidiate

# def IEWMC(MV_field, F1, F2, dist, pad_size, min_block_size, upscale_MV):
        Ff, Ef = IEWMC(self.fwr_MV_field, source_frame, target_frame, dist, self.pad_size, self.min_block_size, self.upscale_MV)
        Fb, Eb = IEWMC(self.bwr_MV_field, target_frame, source_frame, 1-dist, self.pad_size, self.min_block_size, self.upscale_MV)
        
        #Get combined frame
        Fc = Error_adaptive_combination(Ff, Ef, Fb, Eb)

        #Fill holes in the combined frame
        Fc_filled = BDHI(Fc, self.min_block_size, self.pad_size)

        #self.show_images(Ff,Fb,Fc,Fc_filled)


        #Remove padding
        Out_frame = unpad_and_downconvert(Fc_filled, self.pad_size)

        return Out_frame









    def plot_vector_field(self,source_frame):
        import matplotlib.pyplot as plt
        #Downsample so each vector represents one block.
        if self.upscale_MV == False:
            Down_sampled_MV = self.MV_field
            X, Y = np.meshgrid(np.linspace(0,(self.MV_field.shape[1]*self.min_block_size)-1, Down_sampled_MV.shape[1]), \
                                np.linspace(0,(self.MV_field.shape[0]*self.min_block_size) -1, Down_sampled_MV.shape[0]))
        else :
            Down_sampled_MV=self.MV_field[::self.min_block_size,::self.min_block_size,:]
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
        plt.title("Block size="+str(self.min_block_size)+ "\nSteps="+str(self.steps))
        plt.show()

    def show_images(self, Ff, Fb, Fc, Fc_filled):
        import matplotlib.pyplot as plt
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

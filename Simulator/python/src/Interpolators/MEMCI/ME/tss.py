import numpy as np
import math
from imageio import imread, imwrite
import sys
import cProfile
import time
from numba import jit, uint32, float32, int8, int32, uint8, int64, types, config
# from .plot_mv import plot_vector_field

@jit(float32[:,:,:](int32, int32, int32[:], types.UniTuple(uint32, 3), uint8[:,:,:], uint8[:,:,:], float32[:,:,:]), nopython=True)
def helper(block_size, steps, prec_dic, frame_shape, source_frame_pad, target_frame_pad, output):
    for s_row in range(0, frame_shape[0], block_size):
        for s_col in range(0, frame_shape[1], block_size):
            source_block = source_frame_pad[s_row:s_row+block_size, s_col:s_col+block_size, :]
            center_sad = None
            lowest_sad = math.inf
            lowest_idx = (0, 0)
            lowest_i = 0
            curr_row = s_row
            curr_col = s_col
            for step in range(steps, 0, -1):
                S = 2 ** (step - 1)
                i = -1

                if s_row + block_size >= frame_shape[0]:
                    target_max_row = s_row + 1
                else:
                    target_max_row = frame_shape[0] - block_size
                if s_col + block_size >= frame_shape[0]:
                    target_max_col = s_col + 1
                else:
                    target_max_col = frame_shape[1] - block_size

                for t_row in range(curr_row - S, curr_row + S + 1, S):
                    for t_col in range(curr_col - S, curr_col + S + 1, S):
                        i += 1
                        if (t_row != curr_row or t_col != curr_col or center_sad == None) and (t_row >= 0 and t_row <= target_max_row and t_col >= 0 and t_col <= target_max_col):
                            target_block = target_frame_pad[t_row:t_row+block_size, t_col:t_col+block_size, :]
                            sad = np.sum(np.abs(np.subtract(source_block, target_block)))
                            if sad < lowest_sad or (sad == lowest_sad and prec_dic[i] > prec_dic[lowest_i]):
                                lowest_sad = sad
                                lowest_idx = (t_row, t_col)
                                lowest_i = i
                curr_row = lowest_idx[0]
                curr_col = lowest_idx[1]
                center_sad = lowest_sad
            output[s_row:s_row+block_size, s_col:s_col+block_size, 0] = lowest_idx[0] - s_row
            output[s_row:s_row+block_size, s_col:s_col+block_size, 1] = lowest_idx[1] - s_col
            output[s_row:s_row+block_size, s_col:s_col+block_size, 2] = lowest_sad
    return output

def get_motion_vectors(block_size, steps, im1, im2):
    source_frame=im1
    target_frame=im2
    prec_dic = np.array([1, 2, 1, 2, 3, 2, 1, 2, 1], dtype=np.int32)

    frame_shape = source_frame.shape

    source_frame_pad = np.pad(source_frame, ((0,block_size), (0,block_size), (0,0)))  # to allow for non divisible block sizes
    target_frame_pad = np.pad(target_frame, ((0,block_size), (0,block_size), (0,0)))

    output = np.zeros_like(source_frame, dtype='float32')

    output = helper(block_size, steps, prec_dic, frame_shape, source_frame_pad, target_frame_pad, output)
    return output

if __name__ == "__main__":
    if sys.argv[1] == '-f':
        csv_path = sys.argv[2]
        image_height = int(sys.argv[3])
        image_width = int(sys.argv[4])
        out_path = sys.argv[5]
        output = np.genfromtxt(csv_path, delimiter=',').reshape((image_height, image_width, 3))
    else:
        block_size = int(sys.argv[1])
        steps = int(sys.argv[2])
        im1 = imread(sys.argv[3])[:,:,:3]
        im2 = imread(sys.argv[4])[:,:,:3]
        out_path = sys.argv[5]
        output = get_motion_vectors(block_size, steps, im1, im2)
        # np.savetxt(out_path + "/out.csv", output.reshape(-1), delimiter=',')

    # plot_vector_field(output, block_size, out_path)

    # output_intensity = np.copy(output)
    # max_intensity = 0
    # for i in range(output_intensity.shape[0]):
    #     for j in range(output_intensity.shape[1]):
    #         intensity = float(output_intensity[i,j,0]) ** 2.0 + float(output_intensity[i,j,1]) ** 2.0
    #         if intensity > max_intensity:
    #             max_intensity = intensity
    #         output_intensity[i,j,:] = [intensity, intensity, intensity]
    # output_intensity = 255 - (output_intensity * (255.0 / float(max_intensity)))
    # imwrite(out_path, output_intensity)



# im1 = imread("../interpolation-samples/still_frames/eg1/frame1.png")[:,:,:3]
# im2 = imread("../interpolation-samples/still_frames/eg1/frame2.png")[:,:,:3]
# cProfile.run('get_motion_vectors(40, 300, im1, im2)')

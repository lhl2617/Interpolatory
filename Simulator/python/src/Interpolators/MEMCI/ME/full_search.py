import numpy as np
import math
from imageio import imread, imwrite
import time
import sys
import cProfile
# from .plot_mv import plot_vector_field

'''
block_size = size of block used in source and target frame
target_region = number of pixels padding the block to be searched
'''
def get_motion_vectors(block_size, target_region, im1, im2):
    source_frame=im1
    target_frame=im2
    lowest_sad_const = math.inf    # maximum sad score for a block
    lowest_distance_const = math.inf

    source_frame_pad = np.pad(source_frame, ((0,block_size), (0,block_size), (0,0)))  # to allow for non divisible block sizes
    target_frame_pad = np.pad(target_frame, ((0,block_size), (0,block_size), (0,0)))

    output = np.zeros_like(source_frame, dtype='float32')

    for s_row in range(0, source_frame.shape[0], block_size):
        # print(s_row)
        for s_col in range(0, source_frame.shape[1], block_size):
            source_block = source_frame_pad[s_row:s_row+block_size, s_col:s_col+block_size, :]
            lowest_sad = lowest_sad_const
            lowest_distance = lowest_distance_const
            target_index = (0, 0)

            if s_row + block_size >= source_frame.shape[0]:
                target_max_row = s_row + 1
            else:
                target_max_row = source_frame.shape[0] - block_size
            if s_col + block_size >= source_frame.shape[0]:
                target_max_col = s_col + 1
            else:
                target_max_col = source_frame.shape[1] - block_size

            for t_row in range(max(0, s_row - target_region), min(target_max_row, s_row + target_region + 1)):
                for t_col in range(max(0, s_col - target_region), min(target_max_col, s_col + target_region + 1)):
                    target_block = target_frame_pad[t_row:t_row+block_size, t_col:t_col+block_size, :]
                    sad = np.sum(np.abs(np.subtract(source_block, target_block)))
                    distance = (s_row - t_row) *  (s_row - t_row) + (s_col - t_col) * (s_col - t_col)
                    if sad < lowest_sad or (sad == lowest_sad and distance < lowest_distance):
                        lowest_distance = distance
                        lowest_sad = sad
                        target_index = (t_row, t_col)
            output[s_row:s_row+block_size, s_col:s_col+block_size, 0] = target_index[0] - s_row
            output[s_row:s_row+block_size, s_col:s_col+block_size, 1] = target_index[1] - s_col
            output[s_row:s_row+block_size, s_col:s_col+block_size, 2] = lowest_sad

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
        region = int(sys.argv[2])
        im1 = imread(sys.argv[3])[:,:,:3]
        im2 = imread(sys.argv[4])[:,:,:3]
        out_path = sys.argv[5]
        output = get_motion_vectors(block_size, region, im1, im2)
        # np.savetxt(out_path + "/out.csv", output.reshape(-1), delimiter=',')

    plot_vector_field(output, block_size, out_path)



# im1 = imread("../interpolation-samples/still_frames/eg1/frame1.png")[:,:,:3]
# im2 = imread("../interpolation-samples/still_frames/eg1/frame2.png")[:,:,:3]
# cProfile.run('get_motion_vectors(40, 300, im1, im2)')

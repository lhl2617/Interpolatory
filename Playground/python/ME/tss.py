import numpy as np
import math
from imageio import imread, imwrite
import sys
import cProfile  
import time
from plot_mv import plot_vector_field

def get_motion_vectors(block_size, steps, source_frame, target_frame):
    output = np.empty_like(source_frame, dtype='float32')
    prec_dic = [1, 2, 1, 2, 3, 2, 1, 2, 1]

    prev_time = time.time()
    for s_row in range(0, source_frame.shape[0], block_size):
        print(s_row, time.time() - prev_time)
        prev_time = time.time()
        for s_col in range(0, source_frame.shape[1], block_size):
            source_block = source_frame[s_row:s_row+block_size, s_col:s_col+block_size, :]
            center_sad = None
            lowest_sad = 9999999999999
            lowest_idx = (0, 0)
            lowest_i = 0
            curr_row = s_row
            curr_col = s_col
            for step in range(steps, 0, -1):
                S = 2 ** (step - 1)
                i = 0
                for t_row in range(curr_row - S, curr_row + S, S):
                    for t_col in range(curr_col - S, curr_col + S, S):
                        i += 1
                        if (t_row != curr_row or t_col != curr_col or center_sad == None) and (t_row >= 0 and t_row <= source_frame.shape[0] - block_size and t_col >= 0 and t_col <= source_frame.shape[1] - block_size):
                            target_block = target_frame[t_row:t_row+block_size, t_col:t_col+block_size, :]
                            sad = np.sum(np.abs(np.subtract(source_block, target_block)))
                            if sad < lowest_sad or (sad == lowest_sad and prec_dic[i] > prec_dic[lowest_i]):
                                lowest_sad = sad
                                lowest_idx = (t_row, t_col)
                                lowest_i = i
                curr_row = lowest_idx[0]
                curr_col = lowest_idx[1]
                center_sad = lowest_sad
            block = np.full((block_size, block_size, 3), [lowest_idx[0] - s_row, lowest_idx[1] - s_col, lowest_sad])
            output[s_row:s_row+block_size, s_col:s_col+block_size, :] = block
            
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

    plot_vector_field(output, block_size, out_path)

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
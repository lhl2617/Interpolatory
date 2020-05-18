import numpy as np
import math
from imageio import imread, imwrite
import sys
import cProfile  
import time

def get_motion_vectors(block_size, steps, source_frame, target_frame):
    output = np.empty_like(source_frame, dtype='float32')
    # prec_dic = [1, 2, 1, 2, 3, 2, 1, 2, 1]

    prev_time = time.time()
    for s_row in range(0, source_frame.shape[0], block_size):
        print(s_row, time.time() - prev_time)
        prev_time = time.time()
        for s_col in range(0, source_frame.shape[1], block_size):
            source_block = source_frame[s_row:s_row+block_size, s_col:s_col+block_size, :]
            center_sad = None
            lowest_idx = (s_row, s_col)
            for step in range(steps, 0, -1):
                S = 2 ** (step - 1)

                # centre, right, down
                # depending on quadrant, more searches
                if center_sad == None:
                    center_block = target_frame[lowest_idx[0]:lowest_idx[0]+block_size, lowest_idx[1]:lowest_idx[1]+block_size, :]
                    center_sad = np.sum(np.abs(np.subtract(source_block, center_block)))
                right_block = target_frame[lowest_idx[0]:lowest_idx[0]+block_size, lowest_idx[1]+S:lowest_idx[1]+block_size+S, :]
                right_sad = np.sum(np.abs(np.subtract(source_block, right_block)))
                down_block = target_frame[lowest_idx[0]+S:lowest_idx[0]+S+block_size, lowest_idx[1]:lowest_idx[1]+block_size, :]
                down_sad = np.sum(np.abs(np.subtract(source_block, down_block)))

                if center_sad >= right_sad:
                    if center_sad >= down_sad:
                        right_down_block = target_frame[lowest_idx[0]+S:lowest_idx[0]+S+block_size, lowest_idx[1]+S:lowest_idx[1]+S+block_size, :]
                        right_down_sad = np.sum(np.abs(np.subtract(source_block, right_down_block)))
                        if right_sad <= down_sad and right_sad <= right_down_sad:
                            center_sad = right_sad
                            lowest_idx = (lowest_idx[0], lowest_idx[1]+S)
                        elif down_sad <= right_sad and down_sad <= right_down_sad:
                            center_sad = down_sad
                            lowest_idx = (lowest_idx[0]+S, lowest_idx[1])
                        else:
                            center_sad = right_down_sad
                            lowest_idx = (lowest_idx[0]+S, lowest_idx[1]+S)
                    else:
                        up_block = target_frame[lowest_idx[0]-S:lowest_idx[0]-S+block_size, lowest_idx[1]:lowest_idx[1]+block_size, :]
                        up_sad = np.sum(np.abs(np.subtract(source_block, up_block)))
                        right_up_block = target_frame[lowest_idx[0]-S:lowest_idx[0]-S+block_size, lowest_idx[1]+S:lowest_idx[1]+S+block_size, :]
                        right_up_sad = np.sum(np.abs(np.subtract(source_block, right_up_block)))
                        if right_sad <= up_sad and right_sad <= right_up_sad:
                            center_sad = right_sad
                            lowest_idx = (lowest_idx[0], lowest_idx[1]+S)
                        elif up_sad <= right_sad and up_sad <= right_up_sad:
                            center_sad = up_sad
                            lowest_idx = (lowest_idx[0]-S, lowest_idx[1])
                        else:
                            center_sad = right_up_sad
                            lowest_idx = (lowest_idx[0]-S, lowest_idx[1]+S)
                else:
                    if center_sad >= down_sad:
                        left_block = target_frame[lowest_idx[0]:lowest_idx[0]+block_size, lowest_idx[1]-S:lowest_idx[1]-S+block_size, :]
                        left_sad = np.sum(np.abs(np.subtract(source_block, left_block)))
                        left_down_block = target_frame[lowest_idx[0]+S:lowest_idx[0]+S+block_size, lowest_idx[1]-S:lowest_idx[1]-S+block_size, :]
                        left_down_sad = np.sum(np.abs(np.subtract(source_block, left_down_block)))
                        if left_sad <= down_sad and left_sad <= left_down_sad:
                            center_sad = left_sad
                            lowest_idx = (lowest_idx[0], lowest_idx[1]-S)
                        elif down_sad <= left_sad and down_sad <= left_down_sad:
                            center_sad = down_sad
                            lowest_idx = (lowest_idx[0]+S, lowest_idx[1])
                        else:
                            center_sad = left_down_sad
                            lowest_idx = (lowest_idx[0]+S, lowest_idx[1]-S)
                    else:
                        left_block = target_frame[lowest_idx[0]:lowest_idx[0]+block_size, lowest_idx[1]-S:lowest_idx[1]-S+block_size, :]
                        left_sad = np.sum(np.abs(np.subtract(source_block, left_block)))
                        up_block = target_frame[lowest_idx[0]-S:lowest_idx[0]-S+block_size, lowest_idx[1]:lowest_idx[1]+block_size, :]
                        up_sad = np.sum(np.abs(np.subtract(source_block, up_block)))
                        left_up_block = target_frame[lowest_idx[0]-S:lowest_idx[0]-S+block_size, lowest_idx[1]-S:lowest_idx[1]-S+block_size, :]
                        left_up_sad = np.sum(np.abs(np.subtract(source_block, left_up_block)))
                        if center_sad <= left_sad and center_sad <= up_sad and center_sad <= left_up_sad:
                            center_sad = center_sad
                            lowest_idx = lowest_idx
                        elif left_sad <= center_sad and left_sad <= up_sad and left_sad <= left_up_sad:
                            center_sad = left_sad
                            lowest_idx = (lowest_idx[0], lowest_idx[0]-S)
                        elif up_sad <= center_sad and up_sad <= left_sad and up_sad <= left_up_sad:
                            center_sad = up_sad
                            lowest_idx = (lowest_idx[0]-S, lowest_idx[1])
                        else:
                            center_sad = left_up_sad
                            lowest_idx = (lowest_idx[0]-S, lowest_idx[1]-S)

            block = np.full((block_size, block_size, 3), [lowest_idx[0] - s_row, lowest_idx[1] - s_col, center_sad])
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
        np.savetxt(out_path + "/out.csv", output.reshape(-1), delimiter=',')

    output_intensity = np.copy(output)
    max_intensity = 0
    for i in range(output_intensity.shape[0]):
        for j in range(output_intensity.shape[1]):
            intensity = float(output_intensity[i,j,0]) ** 2.0 + float(output_intensity[i,j,1]) ** 2.0
            if intensity > max_intensity:
                max_intensity = intensity
            output_intensity[i,j,:] = [intensity, intensity, intensity]
    output_intensity = 255 - (output_intensity * (255.0 / float(max_intensity)))
    imwrite(out_path + "/out_intensity.png", output_intensity)



# im1 = imread("../interpolation-samples/still_frames/eg1/frame1.png")[:,:,:3]
# im2 = imread("../interpolation-samples/still_frames/eg1/frame2.png")[:,:,:3]
# cProfile.run('get_motion_vectors(40, 300, im1, im2)')
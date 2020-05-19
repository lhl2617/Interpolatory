import numpy as np
from imageio import imread, imwrite
import sys
import time
from plot_mv import plot_vector_field
from full_search import get_motion_vectors as full_search

# image = imread('../IntelVideoInterpolation/Playground/interpolation-samples/still_frames/eg2/frame1.png')[:,:,:3]
# out_path = '../IntelVideoInterpolation/Playground/interpolation-samples/still_frames/eg2/downsampled_05.png'

# steps = 3

# a = 0.5
# w = np.array([0.25 - a/2, 0.25, a, 0.25, 0.25 - a/2])
# weightings = np.zeros((5,5,3))
# for i in range(5):
#     for j in range(5):
#         weightings[i,j,:] = w[i]*w[j]

# # print(weightings)

# t = time.time()

# for s in range(steps):
#     next_image = np.zeros((image.shape[0]>>1, image.shape[1]>>1, image.shape[2]))
#     print('step:',s)
#     for row in range(2, image.shape[0]-2, 2):
#         for col in range(2, image.shape[1]-2, 2):
#             next_image[row>>1, col>>1] = np.sum(weightings * image[row - 2 : row + 3, col - 2 : col + 3], axis=(0,1))
#     image = next_image
#     print('time:',time.time()-t)
#     t=time.time()

# imwrite(out_path, image)

# down scale and store images
# use full search to calculate mv for most reduced image
# calculate mvs for next level up using previous mvs

def downscale(image, weightings):
    padded = np.pad(image, 1)[:,:,1:4]
    out = np.zeros((image.shape[0]>>1, image.shape[1]>>1, 3))
    for row in range(0, image.shape[0], 2):
        for col in range(0, image.shape[1], 2):
            pad_row = row + 1
            pad_col = col + 1
            out[row>>1, col>>1] = np.sum(weightings * padded[pad_row - 1 : pad_row + 2, pad_col - 1 : pad_col + 2], axis=(0,1))
    return out

def blockwise_fs(block1, block2, vec):
    if block2.shape[0] != block1.shape[0] + 2 or block2.shape[1] != block2.shape[1] + 2:
        return vec, 99999999999
    sad_left_up = np.sum(np.abs(block1 - block2[0 : block2.shape[0], 0 : block2.shape[1]]))
    sad_up = np.sum(np.abs(block1 - block2[0 : block2.shape[0], 1 : block2.shape[1] + 1]))
    sad_right_up = np.sum(np.abs(block1 - block2[0 : block2.shape[0], 2 : block2.shape[1] + 2]))
    sad_left = np.sum(np.abs(block1 - block2[1 : block2.shape[0] + 1, 0 : block2.shape[1]]))
    sad_center = np.sum(np.abs(block1 - block2[1 : block2.shape[0] + 1, 0 : block2.shape[1] + 1]))
    sad_right = np.sum(np.abs(block1 - block2[1 : block2.shape[0] + 1, 2 : block2.shape[1] + 2]))
    sad_left_down = np.sum(np.abs(block1 - block2[3 : block2.shape[0] + 3, 0 : block2.shape[1]]))
    sad_down = np.sum(np.abs(block1 - block2[3 : block2.shape[0] + 3, 1 : block2.shape[1] + 1]))
    sad_right_down = np.sum(np.abs(block1 - block2[3 : block2.shape[0] + 3, 2 : block2.shape[1] + 2]))
    min_sad = min(sad_left_up, sad_up, sad_right_up, sad_left, sad_center, sad_right, sad_left_down, sad_down, sad_right_down)
    ret = 0
    if sad_center == min_sad:
        ret = vec
    elif sad_left == min_sad:
        ret = vec + (0, -1)
    elif sad_right == min_sad:
        ret = vec + (0, 1)
    elif sad_up == min_sad:
        ret = vec + (-1, 0)
    elif sad_down == min_sad:
        ret = vec + (1, 0)
    elif sad_left_up == min_sad:
        ret = vec + (-1, -1)
    elif sad_right_up == min_sad:
        ret = vec + (-1, 1)
    elif sad_left_down == min_sad:
        ret = vec + (1, -1)
    else:
        ret = vec + (1, 1)
    return ret, min_sad

def get_motion_vectors(block_size, region, im1, im2):
    w = np.array([0.25, 0.5, 0.25])
    weightings = np.zeros((3,3,3))
    for i in range(3):
        for j in range(3):
            weightings[i,j,:] = w[i]*w[j]

    im1_lst = [im1, 0, 0, 0]
    im2_lst = [im2, 0, 0, 0]
    for i in range(1, 4):
        im1_lst[i] = downscale(im1_lst[i-1], weightings)
        im2_lst[i] = downscale(im2_lst[i-1], weightings)

    mvs = full_search(block_size, region, im1_lst[2], im2_lst[2])

    for s in range(1, -1, -1):
        next_mvs = np.zeros_like(im1_lst[s])
        for row in range(0, next_mvs.shape[0], block_size << 1):
            for col in range(0, next_mvs.shape[1], block_size << 1):
                for i in range(2):
                    for j in range(2):
                        block = im1_lst[s][row + i*block_size : row + (i+1)*block_size, col + j*block_size : col + (j+1)*block_size, :]
                        father_vec = mvs[row >> 1, col >> 1, 0], mvs[row >> 1, col >> 1, 1]
                        father_block = im2_lst[s][int(row + i*block_size + father_vec[0]) : int(row + (i+1)*block_size + father_vec[0]), int(col + j*block_size + father_vec[1]) : int(col + (j+1)*block_size + father_vec[1]), :]
                        father = blockwise_fs(block, father_block, father_vec)
                        
                        up_row = (row >> 1) - block_size
                        up_col = col >> 1
                        if up_row < 0 or up_row >= mvs.shape[0] or up_col < 0 or up_col >= mvs.shape[1]:
                            up = ((0,0), 99999999999)
                        else:
                            up_vec = mvs[(row >> 1) - block_size, (col >> 1), 0], mvs[(row >> 1) - block_size, (col >> 1), 1]
                            up_block = im2_lst[s][int(row + i*block_size + up_vec[0]) : int(row + (i+1)*block_size + up_vec[0]), int(col + j*block_size + up_vec[1]) : int(col + (j+1)*block_size + up_vec[1]), :]
                            up = blockwise_fs(block, up_block, up_vec)

                        right_row = row >> 1 
                        right_col = (col >> 1) + block_size
                        if right_row < 0 or right_row >= mvs.shape[0] or right_col < 0 or right_col >= mvs.shape[1]:
                            right = ((0,0), 99999999999)
                        else:
                            right_vec = mvs[(row >> 1), (col >> 1) + block_size, 0], mvs[(row >> 1), (col >> 1) + block_size, 1]
                            right_block = im2_lst[s][int(row + i*block_size + right_vec[0]) : int(row + (i+1)*block_size + right_vec[0]), int(col + j*block_size + right_vec[1]) : int(col + (j+1)*block_size + right_vec[1]), :]
                            right = blockwise_fs(block, right_block, right_vec)

                        if father[1] <= up[1] and father[1] <= right[1]:
                            next_mvs[row + i*block_size : row + (i+1)*block_size, col + j*block_size : col + (j+1)*block_size, 0] = father[0][0]
                            next_mvs[row + i*block_size : row + (i+1)*block_size, col + j*block_size : col + (j+1)*block_size, 1] = father[0][1]
                            next_mvs[row + i*block_size : row + (i+1)*block_size, col + j*block_size : col + (j+1)*block_size, 2] = father[1]
                        elif up[1] <= right[1]:
                            next_mvs[row + i*block_size : row + (i+1)*block_size, col + j*block_size : col + (j+1)*block_size, 0] = up[0][0]
                            next_mvs[row + i*block_size : row + (i+1)*block_size, col + j*block_size : col + (j+1)*block_size, 1] = up[0][1]
                            next_mvs[row + i*block_size : row + (i+1)*block_size, col + j*block_size : col + (j+1)*block_size, 2] = up[1]
                        else:
                            next_mvs[row + i*block_size : row + (i+1)*block_size, col + j*block_size : col + (j+1)*block_size, 0] = right[0][0]
                            next_mvs[row + i*block_size : row + (i+1)*block_size, col + j*block_size : col + (j+1)*block_size, 1] = right[0][1]
                            next_mvs[row + i*block_size : row + (i+1)*block_size, col + j*block_size : col + (j+1)*block_size, 2] = right[1]
        mvs = next_mvs

    return mvs

if __name__ == "__main__":
    block_size = int(sys.argv[1])
    region = int(sys.argv[2])
    im1 = imread(sys.argv[3])[:,:,:3]
    im2 = imread(sys.argv[4])[:,:,:3]
    out_path = sys.argv[5]
    output = get_motion_vectors(block_size, region, im1, im2)

    print('Printing output...')
    plot_vector_field(output, block_size, out_path)
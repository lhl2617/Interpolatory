import numpy as np
from imageio import imread, imwrite
import sys
import time
from plot_mv import plot_vector_field
from full_search import get_motion_vectors as full_search
from tss import get_motion_vectors as tss
from scipy.ndimage import convolve
import math

# def downscale(image, weightings):
#     return convolve(image / 255.0, weightings, mode='constant')[::2, ::2] * 255.0

# def blockwise_fs(block1, block2, vec):
#     if block2.shape[0] != block1.shape[0] + 2 or block2.shape[1] != block2.shape[1] + 2:
#         return vec, 99999999999
#     sad_left_up = np.sum(np.abs(block1 - block2[0 : block2.shape[0], 0 : block2.shape[1]]))
#     sad_up = np.sum(np.abs(block1 - block2[0 : block2.shape[0], 1 : block2.shape[1] + 1]))
#     sad_right_up = np.sum(np.abs(block1 - block2[0 : block2.shape[0], 2 : block2.shape[1] + 2]))
#     sad_left = np.sum(np.abs(block1 - block2[1 : block2.shape[0] + 1, 0 : block2.shape[1]]))
#     sad_center = np.sum(np.abs(block1 - block2[1 : block2.shape[0] + 1, 0 : block2.shape[1] + 1]))
#     sad_right = np.sum(np.abs(block1 - block2[1 : block2.shape[0] + 1, 2 : block2.shape[1] + 2]))
#     sad_left_down = np.sum(np.abs(block1 - block2[3 : block2.shape[0] + 3, 0 : block2.shape[1]]))
#     sad_down = np.sum(np.abs(block1 - block2[3 : block2.shape[0] + 3, 1 : block2.shape[1] + 1]))
#     sad_right_down = np.sum(np.abs(block1 - block2[3 : block2.shape[0] + 3, 2 : block2.shape[1] + 2]))
#     min_sad = min(sad_left_up, sad_up, sad_right_up, sad_left, sad_center, sad_right, sad_left_down, sad_down, sad_right_down)
#     ret = 0
#     if sad_center == min_sad:
#         ret = vec
#     elif sad_left == min_sad:
#         ret = (vec[0], vec[1] - 1)
#     elif sad_right == min_sad:
#         ret = (vec[0], vec[1] + 1)
#     elif sad_up == min_sad:
#         ret = (vec[0] - 1, vec[1])
#     elif sad_down == min_sad:
#         ret = (vec[0] + 1, vec[1])
#     elif sad_left_up == min_sad:
#         ret = (vec[0] - 1, vec[1] - 1)
#     elif sad_right_up == min_sad:
#         ret = (vec[0] - 1, vec[1] + 1)
#     elif sad_left_down == min_sad:
#         ret = (vec[0] + 1, vec[1] - 1)
#     else:
#         ret = (vec[0] + 1, vec[1] + 1)
#     return ret, min_sad

# def get_motion_vectors(block_size, region, im1, im2):
#     w = np.array([0.25, 0.5, 0.25])
#     weightings = np.zeros((3,3))
#     for i in range(3):
#         for j in range(3):
#             weightings[i,j] = w[i]*w[j]
#     weightings = weightings[:, :, None]

#     im1_lst = [im1, 0, 0]
#     im2_lst = [im2, 0, 0]
#     for i in range(1, 3):
#         print('Downscaling level',i)
#         im1_lst[i] = downscale(im1_lst[i-1], weightings)
#         im2_lst[i] = downscale(im2_lst[i-1], weightings)

#     print('Calculating initial FS...')
#     mvs = full_search(block_size, region, im1_lst[2], im2_lst[2])
#     # mvs = tss(block_size, 3, im1_lst[2], im2_lst[2])

#     for s in range(1, -1, -1):
#         print('Propagating back to level',s)
#         next_mvs = np.zeros_like(im1_lst[s], dtype='float32')
#         for row in range(0, next_mvs.shape[0], block_size << 1):
#             for col in range(0, next_mvs.shape[1], block_size << 1):
#                 for i in range(2):
#                     for j in range(2):
#                         block = im1_lst[s][row + i*block_size : row + (i+1)*block_size, col + j*block_size : col + (j+1)*block_size, :]
#                         father_vec = mvs[row >> 1, col >> 1, 0] * 2 - 1, mvs[row >> 1, col >> 1, 1] * 2 - 1
#                         father_block = im2_lst[s][int(row + i*block_size + father_vec[0]) : int(row + (i+1)*block_size + father_vec[0]), int(col + j*block_size + father_vec[1]) : int(col + (j+1)*block_size + father_vec[1]), :]
#                         father = blockwise_fs(block, father_block, (father_vec[0] + 1, father_vec[1] + 1))
                        
#                         up_row = (row >> 1) - block_size
#                         up_col = col >> 1
#                         if up_row < 0 or up_row >= mvs.shape[0] or up_col < 0 or up_col >= mvs.shape[1]:
#                             up = ((0,0), 99999999999)
#                         else:
#                             up_vec = mvs[(row >> 1) - block_size, (col >> 1), 0] * 2 - 1, mvs[(row >> 1) - block_size, (col >> 1), 1] * 2 - 1
#                             up_block = im2_lst[s][int(row + i*block_size + up_vec[0]) : int(row + (i+1)*block_size + up_vec[0]), int(col + j*block_size + up_vec[1]) : int(col + (j+1)*block_size + up_vec[1]), :]
#                             up = blockwise_fs(block, up_block, (up_vec[0] + 1, up_vec[1] + 1))

#                         right_row = row >> 1 
#                         right_col = (col >> 1) + block_size
#                         if right_row < 0 or right_row >= mvs.shape[0] or right_col < 0 or right_col >= mvs.shape[1]:
#                             right = ((0,0), 99999999999)
#                         else:
#                             right_vec = mvs[(row >> 1), (col >> 1) + block_size, 0] * 2 - 1, mvs[(row >> 1), (col >> 1) + block_size, 1] * 2 - 1
#                             right_block = im2_lst[s][int(row + i*block_size + right_vec[0]) : int(row + (i+1)*block_size + right_vec[0]), int(col + j*block_size + right_vec[1]) : int(col + (j+1)*block_size + right_vec[1]), :]
#                             right = blockwise_fs(block, right_block, (right_vec[0] + 1, right_vec[1] + 1))

#                         if father[1] <= up[1] and father[1] <= right[1]:
#                             next_mvs[row + i*block_size : row + (i+1)*block_size, col + j*block_size : col + (j+1)*block_size, 0] = father[0][0]
#                             next_mvs[row + i*block_size : row + (i+1)*block_size, col + j*block_size : col + (j+1)*block_size, 1] = father[0][1]
#                             next_mvs[row + i*block_size : row + (i+1)*block_size, col + j*block_size : col + (j+1)*block_size, 2] = father[1]
#                         elif up[1] <= right[1]:
#                             next_mvs[row + i*block_size : row + (i+1)*block_size, col + j*block_size : col + (j+1)*block_size, 0] = up[0][0]
#                             next_mvs[row + i*block_size : row + (i+1)*block_size, col + j*block_size : col + (j+1)*block_size, 1] = up[0][1]
#                             next_mvs[row + i*block_size : row + (i+1)*block_size, col + j*block_size : col + (j+1)*block_size, 2] = up[1]
#                         else:
#                             next_mvs[row + i*block_size : row + (i+1)*block_size, col + j*block_size : col + (j+1)*block_size, 0] = right[0][0]
#                             next_mvs[row + i*block_size : row + (i+1)*block_size, col + j*block_size : col + (j+1)*block_size, 1] = right[0][1]
#                             next_mvs[row + i*block_size : row + (i+1)*block_size, col + j*block_size : col + (j+1)*block_size, 2] = right[1]
#         mvs = next_mvs
        
#     return mvs

def search_region(block, window, size):
    lowest_sad = math.inf
    lowest_dist = math.inf
    lowest_vec = (0, 0)
    for row in range(window.shape[0] - block.shape[0]):
        for col in range(window.shape[1] - block.shape[1]):
            sad = np.sum(np.abs(block - window[row : row + block.shape[0], col : col + block.shape[1], :]))
            dist = (row - size) * (row - size) + (col - size) * (col - size)
            if sad < lowest_sad or (sad == lowest_sad and dist <= lowest_dist):
                lowest_sad = sad
                lowest_dist = dist
                lowest_vec = (row - size, col - size)
    return lowest_vec, lowest_sad

def get_motion_vectors(block_size, region, sub_region, min_block_size, steps, im1, im2):
    weightings = np.array([
        [0.0625, 0.125, 0.0625],
        [0.125, 0.25, 0.125],
        [0.0625, 0.125, 0.0625]
    ])
    weightings = weightings[:,:,None]

    im1_lst = []
    im2_lst = []
    im1_lst.append(im1)
    im2_lst.append(im2)
    for i in range(1, steps+1):
        print('Downscaling level',i)
        im1_lst.append(convolve(im1_lst[-1] / 255.0, weightings, mode='constant')[::2, ::2] * 255.0)
        im2_lst.append(convolve(im2_lst[-1] / 255.0, weightings, mode='constant')[::2, ::2] * 255.0)
    
    print('Calculating initial motion vectors')
    mvs = full_search(block_size, region, im1_lst[-1], im2_lst[-1])
    # mvs = tss(block_size, 3, im1_lst[-1], im1_lst[-1])

    for s in range(steps - 1, -1, -1):
        print('Propagating back to level', s)
        next_mvs = np.zeros_like(im1_lst[s], dtype='float32')
        for row in range(0, mvs.shape[0], block_size):
            for col in range(0, mvs.shape[1], block_size):
                vecs = []
                vecs.append(mvs[row, col] * 2)  # parent vector (and sad but ignore)
                if col >= block_size:
                    vecs.append(mvs[row, col - block_size] * 2) 
                else:
                    vecs.append(mvs[row, col + block_size] * 2)
                if row >= block_size:
                    vecs.append(mvs[row - block_size, col] * 2)
                else:
                    vecs.append(mvs[row + block_size, col] * 2)
                
                for i in range(row * 2, (row + block_size) * 2, block_size):
                    for j in range(col * 2, (col + block_size) * 2, block_size):
                        lowest_sad = math.inf
                        lowest_vec = (0,0)
                        block = im1_lst[s][i:i+block_size, j:j+block_size, :]
                        for vec in vecs:
                            new_i = i + int(vec[0])
                            new_j = j + int(vec[1])
                            search_window = im2_lst[s][new_i-sub_region:new_i+block_size+sub_region, new_j-sub_region:new_j+block_size+sub_region]
                            result = search_region(block, search_window, sub_region)
                            if result[1] < lowest_sad:
                                lowest_sad = result[1]
                                lowest_vec = (result[0][0] + vec[0], result[0][1] + vec[1])
                        next_mvs[i:i+block_size, j:j+block_size, 0] = lowest_vec[0]
                        next_mvs[i:i+block_size, j:j+block_size, 1] = lowest_vec[1]
                        next_mvs[i:i+block_size, j:j+block_size, 2] = lowest_sad
        mvs = next_mvs


    while(block_size > min_block_size):
        block_size = block_size >> 1
        print('Increasing density with block size', block_size)
        next_mvs = np.zeros_like(im1, dtype='float32')
        for row in range(0, mvs.shape[0], block_size << 1):
            for col in range(0, mvs.shape[1], block_size << 1):
                vecs = []
                vecs.append(mvs[row, col])  # parent vector (and sad but ignore)
                if col >= block_size:
                    vecs.append(mvs[row, col - block_size]) 
                else:
                    vecs.append(mvs[row, col + block_size])
                if row >= block_size:
                    vecs.append(mvs[row - block_size, col])
                else:
                    vecs.append(mvs[row + block_size, col])
                
                for i in range(row, row + (block_size << 1), block_size):
                    for j in range(col, col + (block_size << 1), block_size):
                        lowest_sad = math.inf
                        lowest_vec = (0,0)
                        block = im1[i:i+block_size, j:j+block_size, :]
                        for vec in vecs:
                            new_i = i + int(vec[0])
                            new_j = j + int(vec[1])
                            search_window = im2[new_i-sub_region:new_i+block_size+sub_region, new_j-sub_region:new_j+block_size+sub_region]
                            result = search_region(block, search_window, sub_region)
                            if result[1] < lowest_sad:
                                lowest_sad = result[1]
                                lowest_vec = (result[0][0] + vec[0], result[0][1] + vec[1])
                        next_mvs[i:i+block_size, j:j+block_size, 0] = lowest_vec[0]
                        next_mvs[i:i+block_size, j:j+block_size, 1] = lowest_vec[1]
                        next_mvs[i:i+block_size, j:j+block_size, 2] = lowest_sad
        mvs = next_mvs
                
    return mvs

if __name__ == "__main__":
    block_size = int(sys.argv[1])
    region = int(sys.argv[2])
    sub_region = int(sys.argv[3])
    steps = int(sys.argv[4])
    min_block_size = int(sys.argv[5])
    im1 = imread(sys.argv[6])[:,:,:3]
    im2 = imread(sys.argv[7])[:,:,:3]
    out_path = sys.argv[8]
    output = get_motion_vectors(block_size, region, sub_region, steps, min_block_size, im1, im2)

    print('Printing output...')
    plot_vector_field(output, 4, out_path)
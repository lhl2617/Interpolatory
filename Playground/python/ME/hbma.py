import numpy as np
from imageio import imread, imwrite
import sys
import time
from plot_mv import plot_vector_field
from full_search import get_motion_vectors as full_search
from scipy.ndimage import convolve
import math

def search_region(block, window, size):
    if (window.shape[0] != window.shape[1]):    # for now, if going over boundry, don't search further...
        return (0, 0), 0                        # TODO: think of another way to correct this
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

def get_motion_vectors(block_size, region, sub_region, steps, min_block_size, im1, im2):
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
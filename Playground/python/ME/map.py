import numpy as np
from imageio import imread, imwrite
import sys
import time
from plot_mv import plot_vector_field
from full_search import get_motion_vectors as full_search
from scipy.ndimage import convolve
import math

'''
Produces block-wise motion vectors using ssd
'''
def full_search_ssd(block_size, size, im1, im2):
    im1_pad = np.pad(im1, ((0,block_size), (0,block_size), (0,0)))  # to allow for non divisible block sizes
    im2_pad = np.pad(im2, ((0,block_size), (0,block_size), (0,0)))
    
    mvs = np.zeros_like(im1[::block_size, ::block_size], dtype='float32')
    ssds = np.zeros((mvs.shape[0], mvs.shape[1], 2*size+1, 2*size+1))

    for m_r in range(mvs.shape[0]):
        for m_c in range(mvs.shape[1]):
            s_r = m_r * block_size
            s_c = m_c * block_size
            block = im1_pad[s_r : s_r+block_size, s_c : s_c+block_size, :]
            lowest_ssd = math.inf
            lowest_distance = math.inf
            target_index = (0,0)

            if s_r + block_size >= im1.shape[0]:
                target_max_row = s_r + 1
            else:
                target_max_row = im1.shape[0] - block_size
            if s_c + block_size >= im1.shape[0]:
                target_max_col = s_c + 1
            else:
                target_max_col = im1.shape[1] - block_size

            for t_r in range(max(0, s_r - size), min(target_max_row, s_r + size + 1)):
                for t_c in range(max(0, s_c - size), min(target_max_col, s_c + size + 1)):
                    target_block = im2_pad[t_r : t_r+block_size, t_c : t_c+block_size, :]
                    ssd = np.sum(np.square(np.subtract(block, target_block)))
                    ssds[m_r, m_c, t_r - max(0, s_r - size), t_c - max(0, s_c - size)] = ssd
                    distance = (s_r - t_r) *  (s_r - t_r) + (s_c - t_c) * (s_c - t_c)
                    if ssd < lowest_ssd or (ssd == lowest_ssd and distance < lowest_distance):
                        lowest_distance = distance
                        lowest_ssd = ssd
                        target_index = (t_r, t_c)
            mvs[m_r, m_c, 0] = target_index[0] - s_r
            mvs[m_r, m_c, 1] = target_index[1] - s_c
            mvs[m_r, m_c, 2] = lowest_ssd

    return mvs, ssds

'''
MAP optimisation of mvs
'''
def MAP(mvs, ssds, Tm, Ta):
    out_mvs = np.zeros_like(mvs)

    # for each mv, need to minimise the sum of SSD and 2*lowest_ssd*(sum of V_c)
    # for each x_u, calculate (x_u - x_v)^2
    # for each y_u, calculate (y_u - y_v)^2
    # for each u, calculate both sets of variances for above values (horizontal and vertical cliques)
    # for each u, divide (x_u - x_v)^2 and (y_u - y_v)^2 by 2*(appropriate var)
    # find vector with overall smallest value (as you go)

    

    return out_mvs

def search_region(block, window, size):
    if (window.shape[0] != window.shape[1]):    # for now, if going over boundry, don't search further...
        return (0, 0), 0                        # TODO: think of another way to correct this
    lowest_ssd = math.inf
    lowest_dist = math.inf
    lowest_vec = (0, 0)
    for row in range(window.shape[0] - block.shape[0]):
        for col in range(window.shape[1] - block.shape[1]):
            ssd = np.sum(np.square(block - window[row : row + block.shape[0], col : col + block.shape[1], :]))
            dist = (row - size) * (row - size) + (col - size) * (col - size)
            if ssd < lowest_ssd or (ssd == lowest_ssd and dist <= lowest_dist):
                lowest_ssd = ssd
                lowest_dist = dist
                lowest_vec = (row - size, col - size)
    return lowest_vec, lowest_ssd

def get_motion_vectors(block_size, region, sub_region, steps, min_block_size, im1, im2, map_steps=0):
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
    mvs, ssds = full_search_ssd(block_size, region, im1_lst[-1], im2_lst[-1])

    for i in range(map_steps):
        print('Applying MAP optimisation', i)
        mvs = MAP(mvs, ssds, 1, 1)

    # convert back to image size for the next stage
    temp = np.zeros_like(im1_lst[-1])
    for r in range(mvs.shape[0]):
        for c in range(mvs.shape[1]):
            temp[r*block_size : (r+1)*block_size, c*block_size : (c+1)*block_size, :] = mvs[r,c,:]
    mvs = temp

    for s in range(steps - 1, -1, -1):
        print('Propagating back to level', s)
        next_mvs = np.zeros_like(im1_lst[s], dtype='float32')
        for row in range(0, mvs.shape[0], block_size):
            for col in range(0, mvs.shape[1], block_size):
                vecs = []
                vecs.append(mvs[row, col] * 2)  # parent vector (and ssd but ignore)
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
                        lowest_ssd = math.inf
                        lowest_vec = (0,0)
                        block = im1_lst[s][i:i+block_size, j:j+block_size, :]
                        for vec in vecs:
                            new_i = i + int(vec[0])
                            new_j = j + int(vec[1])
                            search_window = im2_lst[s][new_i-sub_region:new_i+block_size+sub_region, new_j-sub_region:new_j+block_size+sub_region]
                            result = search_region(block, search_window, sub_region)
                            if result[1] < lowest_ssd:
                                lowest_ssd = result[1]
                                lowest_vec = (result[0][0] + vec[0], result[0][1] + vec[1])
                        next_mvs[i:i+block_size, j:j+block_size, 0] = lowest_vec[0]
                        next_mvs[i:i+block_size, j:j+block_size, 1] = lowest_vec[1]
                        next_mvs[i:i+block_size, j:j+block_size, 2] = lowest_ssd
        mvs = next_mvs

    while(block_size > min_block_size):
        block_size = block_size >> 1
        print('Increasing density with block size', block_size)
        next_mvs = np.zeros_like(im1, dtype='float32')
        for row in range(0, mvs.shape[0], block_size << 1):
            for col in range(0, mvs.shape[1], block_size << 1):
                vecs = []
                vecs.append(mvs[row, col])  # parent vector (and ssd but ignore)
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
                        lowest_ssd = math.inf
                        lowest_vec = (0,0)
                        block = im1[i:i+block_size, j:j+block_size, :]
                        for vec in vecs:
                            new_i = i + int(vec[0])
                            new_j = j + int(vec[1])
                            search_window = im2[new_i-sub_region:new_i+block_size+sub_region, new_j-sub_region:new_j+block_size+sub_region]
                            result = search_region(block, search_window, sub_region)
                            if result[1] < lowest_ssd:
                                lowest_ssd = result[1]
                                lowest_vec = (result[0][0] + vec[0], result[0][1] + vec[1])
                        next_mvs[i:i+block_size, j:j+block_size, 0] = lowest_vec[0]
                        next_mvs[i:i+block_size, j:j+block_size, 1] = lowest_vec[1]
                        next_mvs[i:i+block_size, j:j+block_size, 2] = lowest_ssd
        mvs = next_mvs
                
    return mvs

if __name__ == "__main__":
    block_size = int(sys.argv[1])
    region = int(sys.argv[2])
    sub_region = int(sys.argv[3])
    steps = int(sys.argv[4])
    min_block_size = int(sys.argv[5])
    map_steps = int(sys.argv[6])
    im1 = imread(sys.argv[7])[:,:,:3]
    im2 = imread(sys.argv[8])[:,:,:3]
    out_path = sys.argv[9]
    output = get_motion_vectors(block_size, region, sub_region, steps, min_block_size, im1, im2, map_steps)

    print('Printing output...')
    plot_vector_field(output, im1, min_block_size, out_path)
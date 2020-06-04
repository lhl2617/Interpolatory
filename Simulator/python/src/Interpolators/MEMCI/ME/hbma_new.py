import numpy as np
from imageio import imread, imwrite
import sys
import time
# from plot_mv import plot_vector_field
from scipy.ndimage import convolve
import math

class cost_func:
    def __init__(self, cost):
        self.cost = cost
        self.costs = {
            'sad' : self.sad,
            'ssd' : self.ssd
        }
        if cost not in self.costs:
            raise Exception("Specified cost function not avaialble.")

    def __call__(self, block1, block2):
        return self.costs[self.cost](block1, block2)

    def sad(self, block1, block2):
        return np.sum(np.abs(block1 - block2))

    def ssd(self, block1, block2):
        return np.sum(np.square(block1 - block2))

def block_wise_fs(cost, block1, im, idx, win_size, im_shape):
    if idx[0] >= im_shape[0] or idx[1] >= im_shape[1] or idx[0] < 0 or idx[1] < 0:
        return [0, 0, math.inf]

    lowest_cost = math.inf
    lowest_distance = math.inf
    lowest_vec = [0,0]

    im_r = int(idx[0])
    im_c = int(idx[1])

    block_size = int(block1.shape[0])

    max_r_off = win_size + 1
    min_r_off = -win_size
    max_c_off = win_size + 1
    min_c_off = -win_size

    if im_r + win_size + block_size >= im_shape[0]:
        max_r_off = max(1, im_shape[0] - im_r - block_size)
    if im_r - win_size < 0:
        min_r_off += win_size - im_r
    if im_c + win_size + block_size >= im_shape[1]:
        max_c_off = max(1, im_shape[1] - im_c - block_size)
    if im_c - win_size < 0:
        min_c_off += win_size - im_c

    for r_off in range(min_r_off, max_r_off):
        im_r_off = im_r + r_off
        for c_off in range(min_c_off, max_c_off):
            im_c_off = im_c + c_off
            block2 = im[im_r_off : im_r_off + block_size, im_c_off : im_c_off + block_size, :]
            cost_val = cost(block1, block2)
            distance = r_off * r_off + c_off * c_off
            if cost_val < lowest_cost or (cost_val == lowest_cost and distance < lowest_distance):
                lowest_cost = cost_val
                lowest_distance = distance
                lowest_vec = [r_off, c_off]
    return [lowest_vec[0], lowest_vec[1], lowest_cost]

def full_search(cost, block_size, win_size, im1, im2):
    im1_pad = np.pad(im1, ((0,block_size), (0,block_size), (0,0)))
    im2_pad = np.pad(im2, ((0,block_size), (0,block_size), (0,0)))

    mvs = np.zeros_like(im1[::block_size, ::block_size, :], dtype='float32')

    for row in range(mvs.shape[0]):
        im_r = row * block_size
        for col in range(mvs.shape[1]):
            im_c = col * block_size
            block1 = im1_pad[im_r : im_r + block_size, im_c : im_c + block_size, :]
            mvs[row, col, :] = block_wise_fs(cost, block1, im2_pad, (im_r, im_c), win_size, im2.shape)[:]

    return mvs

def increase_vec_density(cost, mvs, block_size, sub_win_size, im1, im2, vec_scale=1):
    im1_pad = np.pad(im1, ((0,block_size), (0,block_size), (0,0)))
    im2_pad = np.pad(im2, ((0,block_size), (0,block_size), (0,0)))

    out = np.zeros((mvs.shape[0]<<1, mvs.shape[1]<<1, mvs.shape[2]), dtype='float32')

    for row in range(mvs.shape[0]):
        for col in range(mvs.shape[1]):
            vecs = []
            vecs.append(mvs[row, col])  # parent vector (and sad but ignore)
            if col >= 1:
                vecs.append(mvs[row, col - 1] * vec_scale)
            else:
                vecs.append(mvs[row, col + 1] * vec_scale)
            if row >= 1:
                vecs.append(mvs[row - 1, col] * vec_scale)
            else:
                vecs.append(mvs[row + 1, col] * vec_scale)

            for o_r in range(row*2, (row+1)*2):
                im_r = o_r * block_size
                for o_c in range(col*2, (col+1)*2):
                    im_c = o_c * block_size
                    block = im1_pad[im_r : im_r + block_size, im_c : im_c + block_size, :]
                    lowest_cost = math.inf
                    for vec in vecs:
                        res = block_wise_fs(cost, block, im2_pad, (im_r+vec[0], im_c+vec[1]), sub_win_size, im1.shape)
                        if res[2] < lowest_cost:
                            lowest_cost = res[2]
                            out[o_r, o_c, 2] = lowest_cost
                            out[o_r, o_c, :2] = res[:2] + vec[:2]

    return out

def get_motion_vectors(cost, block_size, win_size, sub_win_size, steps, min_block_size, im1, im2):
    weightings = np.array([
        [0.0625, 0.125, 0.0625],
        [0.125, 0.25, 0.125],
        [0.0625, 0.125, 0.0625]
    ])[:,:,None]

    im_lst = []
    im_lst.append((im1,im2))
    for i in range(1, steps+1):
        print('Downscaling level',i)
        down_im1 = convolve(im_lst[-1][0] / 255.0, weightings, mode='constant')[::2, ::2] * 255.0
        down_im2 = convolve(im_lst[-1][1] / 255.0, weightings, mode='constant')[::2, ::2] * 255.0
        im_lst.append((down_im1, down_im2))

    print("Calculating initial motion vectors")
    mvs = full_search(cost, block_size, win_size, im_lst[-1][0], im_lst[-1][1])

    for (curr_im1, curr_im2) in (im_lst[-2 :: -1]):
        print('Propagating back to previous level')
        mvs = increase_vec_density(cost, mvs, block_size, sub_win_size, curr_im1, curr_im2, vec_scale=2)

    while(block_size > min_block_size):
        block_size = block_size >> 1
        print('Increasing density with block size', block_size)
        mvs = increase_vec_density(cost, mvs, block_size, sub_win_size, im1, im2)

    return mvs

def upscale(mvs, block_size, out_shape):
    out = np.zeros(out_shape, dtype='float32')
    for row in range(mvs.shape[0]):
        o_r = row * block_size
        for col in range(mvs.shape[1]):
            o_c = col * block_size
            out[o_r : o_r + block_size, o_c : o_c + block_size, :] = mvs[row, col, :]
    return out

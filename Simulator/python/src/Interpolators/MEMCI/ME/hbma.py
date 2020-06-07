import numpy as np
from imageio import imread, imwrite
import sys
import time
# from plot_mv import plot_vector_field
from scipy.ndimage import convolve
import math 
from numba import float32, jit, int8, types, int32, uint8, uint32

cost_key_map = {
    'sad': 0,
    'ssd': 1
}

#@jit(float32(int8, float32[:,:,:], float32[:,:,:]), nopython=True)
def get_cost(cost_key, block1, block2):
    # sad
    if cost_key == 0:
        return np.sum(np.abs(block1 - block2))
    # ssd
    elif cost_key == 1:
        return np.sum(np.square(block1 - block2))
        # should already throw when trying to get cost_key
    else:
        raise Exception("Specified cost function not available.")
    


#@jit(float32[:](int8, float32[:,:,:], float32[:,:,:], types.UniTuple(int32, 2), int32, types.UniTuple(int32, 3)), nopython=True)
def block_wise_fs(cost_key, block1, im, idx, win_size, im_shape):
    if idx[0] >= im_shape[0] or idx[1] >= im_shape[1] or idx[0] < 0 or idx[1] < 0:
        return np.array([0., 0., math.inf], dtype=np.float32)

    lowest_cost = math.inf
    lowest_distance = math.inf
    lowest_vec = [0, 0]

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
            block2 = np.asarray(im[im_r_off: im_r_off + block_size,
                        im_c_off: im_c_off + block_size, :], dtype=np.float32)
            cost_val = get_cost(cost_key, np.asarray(block1, dtype=np.float32), block2)
            distance = r_off * r_off + c_off * c_off
            if cost_val < lowest_cost or (cost_val == lowest_cost and distance < lowest_distance):
                lowest_cost = cost_val
                lowest_distance = distance
                lowest_vec = [r_off, c_off]

    return np.asarray([lowest_vec[0], lowest_vec[1], lowest_cost], dtype=np.float32)

#@jit(float32[:,:,:](int8, int32, int32, types.UniTuple(uint8, 3), float32[:,:,:], float32[:,:,:]), nopython=True)
def full_search_helper(cost_key, block_size, win_size, im_shape, im1_pad, im2_pad):
    mvs = np.zeros((block_size, block_size, im_shape[2]), dtype=np.float32)

    for row in range(mvs.shape[0]):
        im_r = row * block_size
        for col in range(mvs.shape[1]):
            im_c = col * block_size
            block1 = im1_pad[im_r: im_r + block_size,
                             im_c: im_c + block_size, :]
            mvs[row, col, :] = block_wise_fs(
                cost_key, block1, im2_pad, (im_r, im_c), win_size, im_shape)[:]

    return mvs

def full_search(cost_key, block_size, win_size, im1, im2):
    im1_pad = np.pad(im1, ((0, block_size), (0, block_size), (0, 0)))
    im2_pad = np.pad(im2, ((0, block_size), (0, block_size), (0, 0)))

    im_shape = im1.shape

    return full_search_helper(cost_key, block_size, win_size, im_shape, np.asarray(im1_pad, dtype=np.float32), np.asarray(im2_pad, dtype=np.float32))

#@jit(float32[:,:,:](int8, float32[:,:,:], int32, int32, types.UniTuple(int32, 3), float32[:,:,:], float32[:,:,:], int32),nopython=True)
def increase_vec_density_helper(cost_key, mvs, block_size, sub_win_size, im_shape, im1_pad, im2_pad, vec_scale=1):
    out = np.zeros((mvs.shape[0] << 1, mvs.shape[1]
                    << 1, mvs.shape[2]), dtype=np.float32)

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

            if (row+1)*2*block_size >= im_shape[0]:
                r_max = row*2+1
            else:
                r_max = (row+1)*2
            if (col+1)*2*block_size >= im_shape[1]:
                c_max = col*2+1
            else:
                c_max = (col+1)*2

            for o_r in range(row*2, r_max):
                im_r = o_r * block_size
                for o_c in range(col*2, c_max):
                    im_c = o_c * block_size
                    block = im1_pad[im_r: im_r + block_size,
                                    im_c: im_c + block_size, :]
                    lowest_cost = math.inf
                    for vec in vecs:
                        res = block_wise_fs(
                            cost_key,  np.asarray(block, dtype=np.float32), np.asarray(im2_pad, dtype=np.float32), (im_r+vec[0], im_c+vec[1]), sub_win_size, im_shape)
                        if res[2] < lowest_cost:
                            lowest_cost = res[2]
                            out[o_r, o_c, 2] = lowest_cost
                            out[o_r, o_c, :2] = res[:2] + vec[:2]

    return out

def increase_vec_density(cost_key, mvs, block_size, sub_win_size, im1, im2, vec_scale=1):
    im1_pad = np.pad(im1, ((0, block_size), (0, block_size), (0, 0)))
    im2_pad = np.pad(im2, ((0, block_size), (0, block_size), (0, 0)))

    im_shape = im1.shape

    return increase_vec_density_helper(cost_key, mvs, block_size, sub_win_size, im_shape, np.asarray(im1_pad, dtype=np.float32), np.asarray(im2_pad, dtype=np.float32), vec_scale=1)


def get_motion_vectors(block_size, win_size, sub_win_size, steps, min_block_size, im1, im2, cost_str='sad', upscale=True):
    cost_key = cost_key_map[cost_str]
    weightings = np.array([
        [0.0625, 0.125, 0.0625],
        [0.125, 0.25, 0.125],
        [0.0625, 0.125, 0.0625]
    ])[:, :, None]

    im_lst = []
    im_lst.append((im1, im2))
    for i in range(1, steps+1):
        # print('Downscaling level',i)
        down_im1 = convolve(im_lst[-1][0] / 255.0,
                            weightings, mode='constant')[::2, ::2] * 255.0
        # print(down_im1.shape)
        down_im2 = convolve(im_lst[-1][1] / 255.0,
                            weightings, mode='constant')[::2, ::2] * 255.0
        im_lst.append((down_im1, down_im2))
        # print(down_im2.shape)
    # print("Calculating initial motion vectors")
    mvs = full_search(cost_key, block_size, win_size,
                      im_lst[-1][0], im_lst[-1][1])

    for (curr_im1, curr_im2) in (im_lst[-2:: -1]):
        # print('Propagating back to previous level')
        mvs = increase_vec_density(
            cost_key, mvs, block_size, sub_win_size, curr_im1, curr_im2, vec_scale=2)

    while(block_size > min_block_size):
        block_size = block_size >> 1
        # print('Increasing density with block size', block_size)
        mvs = increase_vec_density(
            cost_key, mvs, block_size, sub_win_size, im1, im2)

    if upscale:
        out = np.zeros_like(im1, dtype=np.float32)
        for row in range(mvs.shape[0]):
            o_r = row * block_size
            for col in range(mvs.shape[1]):
                o_c = col * block_size
                out[o_r: o_r + block_size, o_c: o_c +
                    block_size, :] = mvs[row, col, :]
        return out
    return mvs

# if __name__ == "__main__":
#     cost = sys.argv[1]
#     block_size = int(sys.argv[2])
#     win_size = int(sys.argv[3])
#     sub_win_size = int(sys.argv[4])
#     steps = int(sys.argv[5])
#     min_block_size = int(sys.argv[6])
#     path = sys.argv[7]
#     im1 = imread(path+'/frame1.png')[:,:,:3]
#     im2 = imread(path+'/frame2.png')[:,:,:3]

#     t = time.time()
#     output = get_motion_vectors(block_size, win_size, sub_win_size, steps, min_block_size, im1, im2, cost=cost)
#     print('Time taken:', time.time() - t)

#     print('Printing output...')
#     plot_vector_field(output, im1, min_block_size, path+'/HBMA_'+sys.argv[1]+'_'+sys.argv[2]+'_'+sys.argv[3]+'_'+sys.argv[4]+'_'+sys.argv[5]+'_'+sys.argv[6]+'.png')

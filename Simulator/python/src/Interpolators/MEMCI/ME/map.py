import numpy as np
from imageio import imread, imwrite
import sys
import time
# from plot_mv import plot_vector_field
from scipy.ndimage import convolve
import math

'''
Produces block-wise motion vectors using ssd
'''
def full_search_ssd(block_size, size, im1, im2):
    im1_pad = np.pad(im1, ((0,block_size), (0,block_size), (0,0)))  # to allow for non divisible block sizes
    im2_pad = np.pad(im2, ((0,block_size), (0,block_size), (0,0)))
    
    mvs = np.zeros_like(im1[::block_size, ::block_size], dtype='float32')
    ssds = np.full((mvs.shape[0], mvs.shape[1], 2*size+1, 2*size+1), math.inf, dtype='float32')

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
                    ssds[m_r, m_c, t_r - s_r, t_c - s_c] = ssd
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
def MAP(mvs, ssds, im1, block_size, Tm, Ta):

    # for each mv, need to minimise the sum of SSD and 2*lowest_ssd*(sum of V_c)
    # for each x_u, calculate .5 * (x_u - x_v)^2
    # for each y_u, calculate .5 * (y_u - y_v)^2
    # for each u, calculate both sets of variances for above values (horizontal and vertical cliques)
    # for each u, divide (x_u - x_v)^2 and (y_u - y_v)^2 by appropriate var
    # find V_c by adding 2 tables together and multiplying by l(u,v)
    # find vector with overall smallest value (as you go)

    out_mvs = np.zeros_like(mvs)
    size = int((ssds.shape[2] - 1) / 2)

    for m_r in range(mvs.shape[0]):
        for m_c in range(mvs.shape[1]):
            h_vecs = []     # cliques split into 2 classes: horizontal and vertical
            v_vecs = []     # var calculated seperately for both
            if m_r > 0:
                h_vecs.append((mvs[m_r - 1, m_c, :], np.mean(im1[(m_r-1)*block_size : m_r*block_size, m_c*block_size : (m_c+1)*block_size, :])))
            if m_r < mvs.shape[0] - 1:
                h_vecs.append((mvs[m_r + 1, m_c, :], np.mean(im1[(m_r+1)*block_size : (m_r+2)*block_size, m_c*block_size : (m_c+1)*block_size, :])))
            if m_c > 0:
                v_vecs.append((mvs[m_r, m_c - 1, :], np.mean(im1[m_r*block_size : (m_r+1)*block_size, (m_c-1)*block_size : m_c*block_size, :])))
            if m_c < mvs.shape[1] - 1:
                v_vecs.append((mvs[m_r, m_c + 1, :], np.mean(im1[m_r*block_size : (m_r+1)*block_size, (m_c+1)*block_size : (m_c+2)*block_size, :])))
            g_h_r = {}
            g_h_c = {}
            g_v_r = {}
            g_v_c = {}
            lowest_score = math.inf
            lowest_vec = (0,0)
            lowest_distance = math.inf
            for s_r in range(ssds[m_r, m_c].shape[0]):
                s_r_act = s_r - size
                g_h_r[s_r_act] = {}
                g_v_r[s_r_act] = {}
                for h_vec in h_vecs:
                    g_h_r[s_r_act][h_vec[0][0]] = (s_r_act - h_vec[0][0]) * (s_r_act - h_vec[0][0]) / 2.0
                for v_vec in v_vecs:
                    g_v_r[s_r_act][v_vec[0][0]] = (s_r_act - v_vec[0][0]) * (s_r_act - v_vec[0][0]) / 2.0
                h_var = np.var(np.fromiter(g_h_r[s_r_act].values(), dtype='float32')) 
                v_var = np.var(np.fromiter(g_v_r[s_r_act].values(), dtype='float32'))
                for key, val in g_h_r[s_r_act].items():
                    g_h_r[s_r_act][key] = val / h_var
                for key, val in g_v_r[s_r_act].items():
                    g_v_r[s_r_act][key] = val / v_var
                for s_c in range(ssds[m_r, m_c].shape[1]):
                    s_c_act = s_c - size
                    if s_r == 0:
                        g_h_c[s_c_act] = {}
                        g_v_c[s_c_act] = {}
                        for h_vec in h_vecs:
                            g_h_c[s_c_act][h_vec[0][1]] = (s_c_act - h_vec[0][1]) * (s_c_act - h_vec[0][1]) / 2.0
                        for v_vec in v_vecs:
                            g_v_c[s_c_act][v_vec[0][1]] = (s_c_act - v_vec[0][1]) * (s_c_act - v_vec[0][1]) / 2.0
                        h_var = np.var(np.fromiter(g_h_c[s_c_act].values(), dtype='float32')) 
                        v_var = np.var(np.fromiter(g_v_c[s_c_act].values(), dtype='float32'))
                        for key, val in g_h_c[s_c_act].items():
                            g_h_c[s_c_act][key] = val / h_var
                        for key, val in g_v_c[s_c_act].items():
                            g_v_c[s_c_act][key] = val / v_var
                    intensity_u = np.mean(im1[m_r*block_size : (m_r+1)*block_size, m_c*block_size : (m_c+1)*block_size, :])
                    V_c_total = 0
                    for h_vec in h_vecs:
                        if np.linalg.norm([s_r_act - h_vec[0][0], s_c_act - h_vec[0][1]]) <= Tm or abs(intensity_u - h_vec[1]) <= Ta:
                            V_c_total += g_h_r[s_r_act][h_vec[0][0]] + g_h_c[s_c_act][h_vec[0][1]]
                    for v_vec in v_vecs:
                        if np.linalg.norm([s_r_act - v_vec[0][0], s_c_act - v_vec[0][1]]) <= Tm or abs(intensity_u - v_vec[1]) <= Ta:
                            V_c_total += g_v_r[s_r_act][v_vec[0][0]] + g_v_c[s_c_act][v_vec[0][1]]
                    score = ssds[m_r, m_c, s_r_act, s_c_act] + V_c_total
                    if score < lowest_score:
                        lowest_score = score
                        lowest_vec = (s_r_act, s_c_act)
                        lowest_distance = s_r_act * s_r_act + s_c_act * s_c_act
                    elif score == lowest_score:
                        distance = s_r_act * s_r_act + s_c_act * s_c_act
                        if distance < lowest_distance:
                            lowest_score = score
                            lowest_vec = (s_r_act, s_c_act)
                            lowest_distance = distance
            out_mvs[m_r, m_c, 0] = lowest_vec[0]
            out_mvs[m_r, m_c, 1] = lowest_vec[1]
            out_mvs[m_r, m_c, 2] = lowest_score

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

def get_motion_vectors(block_size, region, sub_region, steps, min_block_size, im1, im2, Tm=1, Ta=1, map_steps=0):
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
        mvs = MAP(mvs, ssds, im1_lst[-1], block_size, Tm, Ta)

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

# if __name__ == "__main__":
#     block_size = int(sys.argv[1])
#     region = int(sys.argv[2])
#     sub_region = int(sys.argv[3])
#     steps = int(sys.argv[4])
#     min_block_size = int(sys.argv[5])
#     map_steps = int(sys.argv[6])
#     # im1 = imread(sys.argv[7])[:,:,:3]
#     # im2 = imread(sys.argv[8])[:,:,:3]
#     # out_path = sys.argv[9]
#     Tm = int(sys.argv[7])
#     Ta = int(sys.argv[8])
#     path = sys.argv[9]
#     im1 = imread(path+'/frame1.png')[:,:,:3]
#     im2 = imread(path+'/frame2.png')[:,:,:3]

#     t = time.time()
#     output = get_motion_vectors(block_size, region, sub_region, steps, min_block_size, im1, im2, Tm=Tm, Ta=Ta, map_steps=map_steps)
#     print('Time taken:', time.time() - t)

#     print('Printing output...')
#     plot_vector_field(output, im1, min_block_size, path+'/'+sys.argv[7]+'_'+sys.argv[8]+'_MAP_'+sys.argv[1]+'_'+sys.argv[2]+'_'+sys.argv[3]+'_'+sys.argv[4]+'_'+sys.argv[5]+'_'+sys.argv[6]+'.png')
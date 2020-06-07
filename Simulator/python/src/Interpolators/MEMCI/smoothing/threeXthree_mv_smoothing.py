import numpy as np
from imageio import imread, imwrite
import sys
import cProfile  
import time
# from ..ME.plot_mv import plot_vector_field
from .median_filter import median_filter
from .mean_filter import mean_filter
from .weighted_mean_filter import weighted_mean_filter
# from full_search import get_motion_vectors as mv_fs
# from tss import get_motion_vectors as mv_tss
# from hbma import get_motion_vectors as hbma

filter_func_dict = {
    'median' : median_filter,
    'mean' : mean_filter,
    'weighted' : weighted_mean_filter
}

def smooth(filter_func, mv_field, block_size):
    out = np.copy(mv_field)
    for row in range(0, mv_field.shape[0], block_size):
        #print(row)
        for col in range(0, mv_field.shape[1], block_size):
            low_row = max(0, int(row - block_size))
            high_row = min(int(row + block_size), mv_field.shape[0]) + 1
            low_col = max(0, int(col - block_size))
            high_col = min(int(col + block_size), mv_field.shape[1]) + 1
            r, c = filter_func(mv_field[low_row:high_row:block_size, low_col:high_col:block_size])
            out[row:row+block_size, col:col+block_size, 0] = r # replace out with mv_field maybe
            out[row:row+block_size, col:col+block_size, 1] = c 
    return out
'''
if __name__ == "__main__":
    filter_type = sys.argv[1]
    method = sys.argv[2]
    block_size = int(sys.argv[3])
    metric = int(sys.argv[4])
    im1 = imread(sys.argv[5])[:,:,:3]
    im2 = imread(sys.argv[6])[:,:,:3]
    out_path = sys.argv[7]
    print('Starting ME...')
    if method == 'fs':
        output = mv_fs(block_size, metric, im1, im2)
    elif method == 'tss':
        output = mv_tss(block_size, metric, im1, im2)
    elif method == 'hbma':
        output = hbma(block_size, metric, 1, 2, im1, im2)

    print('Smoothing vectors')
    output = smooth(filter_func_dict[filter_type], output, block_size)

    plot_vector_field(output, block_size, out_path)
'''

    
    # print('Starting vector intensity image...')
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

    
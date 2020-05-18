import numpy as np
from imageio import imread, imwrite
import sys
import cProfile  
import time
from full_search import get_motion_vectors as mv_fs
from tss import get_motion_vectors as mv_tss

def median_filter(block):
    block_flat = block.reshape(-1, block.shape[-1])
    for i in range(block_flat.shape[0]):
        block_flat[i, 2] = block_flat[i, 0] * block_flat[i, 0] + block_flat[i, 1] * block_flat[i, 1]
    sorted_idx = np.argsort(block_flat[:,2])
    median_idx = sorted_idx[int(sorted_idx.shape[0]/2)]
    if sorted_idx.shape[0] % 2 == 0:
        return block_flat[median_idx, :1]
    else:
        return (block_flat[median_idx, :1] + block_flat[median_idx+1, :1]) / 2.0

def smooth(mv_field, size):
    out = np.copy(mv_field)
    for row in range(mv_field.shape[0]):
        print(row)
        for col in range(mv_field.shape[1]):
            low_row = max(0, int(row - size/2))
            high_row = min(int(row + size/2), mv_field.shape[0])
            low_col = max(0, int(col - size/2))
            high_col = min(int(col + size/2), mv_field.shape[1])
            out[row, col, :1] = median_filter(mv_field[low_row : high_row, low_col : high_col]) # replace out with mv_field maybe 
    return out

if __name__ == "__main__":
    method = sys.argv[1]
    filter_size = int(sys.argv[2])
    block_size = int(sys.argv[3])
    metric = int(sys.argv[4])
    im1 = imread(sys.argv[5])[:,:,:3]
    im2 = imread(sys.argv[6])[:,:,:3]
    out_path = sys.argv[7]
    print('Starting ME...')
    if method == 'fs':
        output = mv_fs(block_size, metric, im1, im2)
    else:
        output = mv_tss(block_size, metric, im1, im2)
    print('Starting motion smoothing...')
    output = smooth(output, filter_size)
    
    print('Starting vector intensity image...')
    output_intensity = np.copy(output)
    max_intensity = 0
    for i in range(output_intensity.shape[0]):
        for j in range(output_intensity.shape[1]):
            intensity = float(output_intensity[i,j,0]) ** 2.0 + float(output_intensity[i,j,1]) ** 2.0
            if intensity > max_intensity:
                max_intensity = intensity
            output_intensity[i,j,:] = [intensity, intensity, intensity]
    output_intensity = 255 - (output_intensity * (255.0 / float(max_intensity)))
    imwrite(out_path, output_intensity)
import numpy as np
from imageio import imread, imwrite
import sys
import cProfile  
import time
from full_search import get_motion_vectors as mv_fs
from tss import get_motion_vectors as mv_tss
from plot_mv import plot_vector_field

def median_filter(block):
    block_flat = block.reshape(-1, block.shape[-1])
    sorted_idx_row = np.argsort(block_flat[:,0])
    sorted_idx_col = np.argsort(block_flat[:,1])
    median_idx_row = sorted_idx_row[int(sorted_idx_row.shape[0]/2)]
    median_idx_col = sorted_idx_col[int(sorted_idx_col.shape[0]/2)]
    row = block_flat[median_idx_row, 0]
    col = block_flat[median_idx_col, 1]
    return (row, col)

def smooth(mv_field, block_size):
    out = np.copy(mv_field)
    for row in range(0, mv_field.shape[0], block_size):
        print(row)
        for col in range(0, mv_field.shape[1], block_size):
            low_row = max(0, int(row - block_size))
            high_row = min(int(row + block_size), mv_field.shape[0]) + 1
            low_col = max(0, int(col - block_size))
            high_col = min(int(col + block_size), mv_field.shape[1]) + 1
            r, c = median_filter(mv_field[low_row:high_row:block_size, low_col:high_col:block_size])
            out[row:row+block_size, col:col+block_size, 0] = r # replace out with mv_field maybe
            out[row:row+block_size, col:col+block_size, 1] = c 
    return out

if __name__ == "__main__":
    method = sys.argv[1]
    block_size = int(sys.argv[2])
    metric = int(sys.argv[3])
    im1 = imread(sys.argv[4])[:,:,:3]
    im2 = imread(sys.argv[5])[:,:,:3]
    out_path = sys.argv[6]
    print('Starting ME...')
    if method == 'fs':
        output = mv_fs(block_size, metric, im1, im2)
    else:
        output = mv_tss(block_size, metric, im1, im2)

    print('Starting motion smoothing...')
    output = smooth(output, block_size)

    plot_vector_field(output, block_size, out_path)
    
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

    
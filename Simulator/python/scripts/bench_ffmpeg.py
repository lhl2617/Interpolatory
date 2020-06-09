# we got the 'middle' frame from ffmpeg, now we get the psnr and ssim of each method combination

import os
import sys
import glob 
import imageio
import skimage
import skimage.metrics
import numpy as np

paths = sorted(glob.glob('../../Output/ffmpeg_test/*/Beanbags.png'))

id_strings = [path.split('/')[-2] for path in paths]

full_results = {}

for id_string in id_strings:
    
    psnr = []
    ssim = []

    paths_to_truth = sorted(glob.glob(f'./benchmarks/middlebury/*/frame10i11.png'))

    for path_to_truth in paths_to_truth:
        middlebury_category = path_to_truth.split('/')[-2]

        im_true = imageio.imread(path_to_truth)

        im_test = imageio.imread(f'../../Output/ffmpeg_test/{id_string}/{middlebury_category}.png')

        
        psnr.append(skimage.metrics.peak_signal_noise_ratio(im_true, im_test, data_range=255))
        ssim.append(skimage.metrics.structural_similarity(im_true, im_test, data_range=255, multichannel=True))


    psnr_mean = np.mean(psnr)
    ssim_mean = np.mean(ssim)

    csv_id_string = id_string.replace('-', ',')
    
    print(f'{csv_id_string},{psnr_mean},{ssim_mean}', flush=True)
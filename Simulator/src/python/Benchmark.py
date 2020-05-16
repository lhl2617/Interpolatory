# Runs against middlebury evaluation set in ./middlebury

from Interpolator import InterpolatorDictionary
import glob
import numpy as np
import imageio
import skimage
import skimage.metrics

psnr = {}
ssim = {}


for interpolator_str, interpolator_obj in InterpolatorDictionary.items():
    psnr[interpolator_str] = []
    ssim[interpolator_str] = []
    for path_to_truth in sorted(glob.glob('../../Datasets/middlebury/*/frame10i11.png')):
        test_name = path_to_truth.split('/')[-2]

        path_1 = path_to_truth.replace('frame10i11', 'frame10')
        path_2 = path_to_truth.replace('frame10i11', 'frame11')

        frame_1 = imageio.imread(path_1)
        frame_2 = imageio.imread(path_2)

        im_true = imageio.imread(path_to_truth)
            
        interpolator = interpolator_obj(2)
        im_test = interpolator.get_benchmark_frame(frame_1, frame_2)

        imageio.imwrite(f'../../Output/middlebury_output/{interpolator_str}_{test_name}.png', im_test)
        
        psnr[interpolator_str].append(skimage.metrics.peak_signal_noise_ratio(im_true, im_test, data_range=255))
        ssim[interpolator_str].append(skimage.metrics.structural_similarity(im_true, im_test, data_range=255, multichannel=True))
    print(interpolator_str)
    print(f'mean psnr: {np.mean(psnr[interpolator_str])}')
    print(f'mean ssim: {np.mean(ssim[interpolator_str])}')

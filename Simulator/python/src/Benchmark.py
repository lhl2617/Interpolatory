# Runs against middlebury evaluation set in ./middlebury

from os import path
import glob
import numpy as np
import imageio
import skimage
import skimage.metrics
import json
import time
import math
import pathlib
from .Interpolator import InterpolatorDictionary
from .Globals import debug_flags
from .util import sToMMSS, getETA, signal_progress


def benchmark(interpolation_mode, block_size, target_region, ME_mode, filter_mode, filter_size,output_path=None):

    #benchmark(MCI_mode, block_size, target_region, ME_mode, filter.mode, filter_size)
    
    psnr = []
    ssim = []

    basedir = pathlib.Path(__file__).parent.parent.absolute()

    paths = sorted(glob.glob(f'{basedir}/benchmarks/middlebury/*/frame10i11.png'))

    cnt_done = 0
    start = int(round(time.time() * 1000))

    for path_to_truth in paths:
        test_name = path_to_truth.split(path.sep)[-2]


        path_1 = path_to_truth.replace('frame10i11', 'frame10')
        path_2 = path_to_truth.replace('frame10i11', 'frame11')

        frame_1 = imageio.imread(path_1)
        frame_2 = imageio.imread(path_2)

        im_true = imageio.imread(path_to_truth)
            
        interpolator = InterpolatorDictionary[interpolation_mode](2)

        im_test = interpolator.get_benchmark_frame(frame_1, frame_2, block_size, target_region, ME_mode, filter_mode, filter_size)


        if (not (output_path is None)):
            output_pathname = path.join(output_path, f'{test_name}.png')
            imageio.imwrite(output_pathname, im_test)

        psnr.append(skimage.metrics.peak_signal_noise_ratio(im_true, im_test, data_range=255))
        ssim.append(skimage.metrics.structural_similarity(im_true, im_test, data_range=255, multichannel=True))


        cnt_done += 1
        pct = str(math.floor(100 * float(cnt_done) / len(paths))).rjust(3, ' ')
        curr = int(round(time.time() * 1000))
        elapsed_seconds = int((curr-start) / 1000)
        elapsed = sToMMSS(elapsed_seconds)
        eta = getETA(elapsed_seconds, cnt_done, len(paths))
        progStr = f'PROGRESS::{pct}%::Frame {cnt_done}/{len(paths)} | Time elapsed: {elapsed} | Estimated Time Left: {eta}'
        signal_progress(progStr)
        
        if debug_flags['debug_benchmark_progress']:
            print(progStr)

    if debug_flags['debug_benchmark_progress']:
        end = int(round(time.time() * 1000))
        print(f'PROGRESS::100%::Completed | Time taken: {sToMMSS((end-start) / 1000)}')

    res = {
        'PSNR': np.mean(psnr),
        'SSIM': np.mean(ssim)
    }

    res_json = json.dumps(res)
    
    if (not (output_path is None)):
        output_pathname = path.join(output_path, 'results.txt')
        f = open(output_pathname, "w")
        f.write(res_json)
        f.close()

    print(res_json)

def benchmarkCNN(interpolation_mode, output_path=None):
    psnr = []
    ssim = []

    basedir = pathlib.Path(__file__).parent.parent.absolute()

    paths = sorted(glob.glob(f'{basedir}/benchmarks/middlebury/*/frame10i11.png'))

    cnt_done = 0
    start = int(round(time.time() * 1000))

    for path_to_truth in paths:
        test_name = path_to_truth.split(path.sep)[-2]


        path_1 = path_to_truth.replace('frame10i11', 'frame10')
        path_2 = path_to_truth.replace('frame10i11', 'frame11')

        frame_1 = imageio.imread(path_1)
        frame_2 = imageio.imread(path_2)

        im_true = imageio.imread(path_to_truth)

        interpolator = InterpolatorDictionary[interpolation_mode](2)
        im_test = interpolator.get_benchmark_frame(frame_1, frame_2)


        if (not (output_path is None)):
            output_pathname = path.join(output_path, f'{test_name}.png')
            imageio.imwrite(output_pathname, im_test)

        psnr.append(skimage.metrics.peak_signal_noise_ratio(im_true, im_test, data_range=255))
        ssim.append(skimage.metrics.structural_similarity(im_true, im_test, data_range=255, multichannel=True))


        cnt_done += 1
        pct = str(math.floor(100 * float(cnt_done) / len(paths))).rjust(3, ' ')
        curr = int(round(time.time() * 1000))
        elapsed_seconds = int((curr-start) / 1000)
        elapsed = sToMMSS(elapsed_seconds)
        eta = getETA(elapsed_seconds, cnt_done, len(paths))
        progStr = f'PROGRESS::{pct}%::Frame {cnt_done}/{len(paths)} | Time elapsed: {elapsed} | Estimated Time Left: {eta}'
        signal_progress(progStr)

        if debug_flags['debug_benchmark_progress']:
            print(progStr)

    if debug_flags['debug_benchmark_progress']:
        end = int(round(time.time() * 1000))
        print(f'PROGRESS::100%::Completed | Time taken: {sToMMSS((end-start) / 1000)}')

    res = {
        'PSNR': np.mean(psnr),
        'SSIM': np.mean(ssim)
    }

    res_json = json.dumps(res)

    if (not (output_path is None)):
        output_pathname = path.join(output_path, 'results.txt')
        f = open(output_pathname, "w")
        f.write(res_json)
        f.close()

    print(res_json)

def get_middle_frame(interpolation_mode, frame_1_path, frame_2_path, output_file_path, ground_truth_path=None):
    
    frame_1 = imageio.imread(frame_1_path)
    frame_2 = imageio.imread(frame_2_path)
    
    interpolator = InterpolatorDictionary[interpolation_mode](2)
    im_test = interpolator.get_benchmark_frame(frame_1, frame_2)

    imageio.imwrite(output_file_path, im_test)

    if (not (ground_truth_path is None)):
        im_true = imageio.imread(ground_truth_path)
        psnr = (skimage.metrics.peak_signal_noise_ratio(im_true, im_test, data_range=255))
        ssim = (skimage.metrics.structural_similarity(im_true, im_test, data_range=255, multichannel=True))
            
        res = {
            'PSNR': psnr,
            'SSIM': ssim
        }

        if (res['PSNR'] == math.inf):
            res['PSNR'] = 'Infinity'
            
    res_json = json.dumps(res)
    
    if (not (output_file_path is None)):
        output_pathname = path.join(output_file_path, 'results.txt')
        f = open(output_pathname, "w")
        f.write(res_json)
        f.close()

    print(json.dumps(res_json))

# def test():
#     psnr = {}
#     ssim = {}


#     for interpolator_str, interpolator_obj in InterpolatorDictionary.items():
#         psnr[interpolator_str] = []
#         ssim[interpolator_str] = []
#         for path_to_truth in sorted(glob.glob('../../Datasets/middlebury/*/frame10i11.png')):
#             test_name = path_to_truth.split('/')[-2]

#             path_1 = path_to_truth.replace('frame10i11', 'frame10')
#             path_2 = path_to_truth.replace('frame10i11', 'frame11')

#             frame_1 = imageio.imread(path_1)
#             frame_2 = imageio.imread(path_2)

#             im_true = imageio.imread(path_to_truth)
                
#             interpolator = interpolator_obj(2)
#             im_test = interpolator.get_benchmark_frame(frame_1, frame_2)

#             imageio.imwrite(f'../../Output/middlebury_output/{interpolator_str}_{test_name}.png', im_test)
            
#             psnr[interpolator_str].append(skimage.metrics.peak_signal_noise_ratio(im_true, im_test, data_range=255))
#             ssim[interpolator_str].append(skimage.metrics.structural_similarity(im_true, im_test, data_range=255, multichannel=True))
#         print(interpolator_str)
#         print(f'mean psnr: {np.mean(psnr[interpolator_str])}')
#         print(f'mean ssim: {np.mean(ssim[interpolator_str])}')
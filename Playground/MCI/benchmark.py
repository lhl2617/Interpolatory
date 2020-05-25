# Runs against middlebury evaluation set in ./middlebury

import torch
from Interpolator import InterpolatorDictionary
import glob
import numpy as np
import imageio
import skimage
import skimage.metrics
import time
import csv

psnr = {}
ssim = {}
Total_time={}
# block_size=[4,6,8,10]
# block_size = [4,6,8,10,12,14,16,24]
# target_region =[3,4,5]
block_size=[8]
target_region=[7]
for b in block_size:
    for t in target_region:
        for interpolator_str, interpolator_obj in InterpolatorDictionary.items():
            psnr[interpolator_str] = []
            ssim[interpolator_str] = []
            Total_time[interpolator_str]=[]
            for path_to_truth in sorted(glob.glob('./middlebury/*/frame10i11.png')):
                print(path_to_truth)
                test_name = path_to_truth.split('/')[-2]
                print(test_name)

                path_1 = path_to_truth.replace('frame10i11', 'frame10')
                path_2 = path_to_truth.replace('frame10i11', 'frame11')

                frame_1 = imageio.imread(path_1)
                frame_2 = imageio.imread(path_2)

                im_true = imageio.imread(path_to_truth)
                # start = time.time()
                interpolator = interpolator_obj(2)
                print(interpolator_obj)

                start = time.time()
                im_test = interpolator.get_benchmark_frame(frame_1, frame_2,b,t)

                end = time.time()
                time_taken = round(end-start,2)
                Total_time[interpolator_str].append(time_taken)
                print("Time taken:",time_taken)

                ME_method = "HBMA_SR1_steps1_min2"
                # block_size = 16
                # target_region = 3
                smooth_method = "Mean_filter"

                imageio.imwrite(f'./Auto_test/{interpolator_str}_{test_name}_{ME_method}_{b}_{t}_{smooth_method}.png', im_test)
                # interpolator.plot_vector_field(4,3,frame_1)
                # imageio.imwrite(
                    # f'./MEMCI_test_output/{interpolator_str}_{test_name}_HBMA_weighted_mean_filter5_16_R7SR1_S3_M4_No_filter.png',im_test)
                # HBMA_weighted_mean_filter5_16_R7SR1_S2_M4

                p=round(skimage.metrics.peak_signal_noise_ratio(im_true, im_test, data_range=255),3)
                s=round(skimage.metrics.structural_similarity(im_true, im_test, data_range=255, multichannel=True),3)
                psnr[interpolator_str].append(p)
                ssim[interpolator_str].append(s)


                # with open('result.csv', 'a', newline='')as file:
                #     csv_writer = csv.writer(file)

                    # csv_writer.writerow([test_name,"HBMA",block_size,"R7 SR1 steps3 minBlockSize4",smooth_method,p,s,time_taken])
                    # csv_writer.writerow([test_name, ME_method,block_size, target_region, smooth_method, p, s, time_taken])
                    # csv_writer.writerow("")

            print(interpolator_str)
            print(f'mean psnr: {np.mean(psnr[interpolator_str])}')
            print(f'mean ssim: {np.mean(ssim[interpolator_str])}')
            print(f'mean time:{np.mean(Total_time[interpolator_str])}')
            with open('../python/Result2.csv', 'a', newline='')as file:
                csv_writer = csv.writer(file)
                csv_writer.writerow(
                    ["MiddleBlurry",ME_method, b, t,smooth_method ,np.mean(psnr[interpolator_str]), np.mean(ssim[interpolator_str]), np.mean(Total_time[interpolator_str])])


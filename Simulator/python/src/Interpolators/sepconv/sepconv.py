from ..base import BaseInterpolator
from ...util import is_power_of_two
import math

class SepConvBase(BaseInterpolator):
    def __init__(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):

        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size)
        '''
        Only supports upscaling by factor of 2
        '''
        if not (self.video_in_path is None):
            if self.rate_ratio < 1:
                raise Exception(f'SepConv only supports upconversion, got conversion rate ratio {self.rate_ratio}')
            if (not is_power_of_two(self.rate_ratio)):
                raise Exception(f'SepConv only supports upconversion ratio that is a power of 2, got conversion rate ratio {self.rate_ratio}')
            
        '''
        we store rate_ratio interpolated frames in cache 
        '''
        self.__sepconv_cache = {}


    def __sepconv_repopulate_cache(self, image_1_idx, image_2_idx):
        '''
        gets the middle frame given two images then populates __sepconv_cache
        recursively call until populated
        '''
        if (image_1_idx + 1 == image_2_idx):
            return

        # assumes the two frames image_1 and image_2 are already in cache
        image_1 = self.__sepconv_cache[image_1_idx]
        image_2 = self.__sepconv_cache[image_2_idx]

        mid_image = self.__sepconv_get_middle_frame(image_1, image_2)
        mid_image_idx = int((image_1_idx + image_2_idx) / 2)

        self.__sepconv_cache[mid_image_idx] = mid_image

        # LHS
        self.__sepconv_repopulate_cache(image_1_idx, mid_image_idx)
        # RHS
        self.__sepconv_repopulate_cache(mid_image_idx, image_2_idx)
        


    def __sepconv_get_middle_frame(self, image_1, image_2):
        import numpy
        import torch
        from .src import run

        tenFirst = torch.FloatTensor(numpy.ascontiguousarray(numpy.array(image_1)[:, :, ::-1].transpose(2, 0, 1).astype(numpy.float32) * (1.0 / 255.0)))
        tenSecond = torch.FloatTensor(numpy.ascontiguousarray(numpy.array(image_2)[:, :, ::-1].transpose(2, 0, 1).astype(numpy.float32) * (1.0 / 255.0)))

        tenOutput = run.estimate(tenFirst, tenSecond)

        out_frame = (tenOutput.clamp(0.0, 1.0).numpy().transpose(1, 2, 0)[:, :, ::-1] * 255.0).astype(numpy.uint8)

        return out_frame

    def get_interpolated_frame(self, idx):
        # if not found in cache
        if not (idx in self.__sepconv_cache):
            self.__sepconv_cache.clear()
            
            # repopulate cache
            image_1_idx = int(idx // self.rate_ratio * self.rate_ratio)
            image_2_idx = int(image_1_idx + self.rate_ratio)
            
            # put the relevant frames in cache first
            frameA_idx = idx // self.rate_ratio
            frameB_idx = frameA_idx + 1
            frameA = self.video_stream.get_frame(int(frameA_idx))
            frameB = self.video_stream.get_frame(int(frameB_idx))
            self.__sepconv_cache[image_1_idx] = frameA
            self.__sepconv_cache[image_2_idx] = frameB

            self.__sepconv_repopulate_cache(image_1_idx, image_2_idx)

        return self.__sepconv_cache[idx]


class SepConvL1(SepConvBase):
    def __init__(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
        from .src import run
        run.arguments_strModel = 'l1'
        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size)

    def __str__(self):
        return 'SepConv - L1'

class SepConvLf(SepConvBase):    
    def __init__(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
        from .src import run
        run.arguments_strModel = 'lf'
        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size)

    def __str__(self):
        return 'SepConv - Lf'



    

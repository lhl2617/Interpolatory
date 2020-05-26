from ..MEMCI.MCI.base import BaseInterpolator, MidFrameBaseInterpolator
from ...Flow import FlowsDictionary
from ...util import get_first_frame_idx_and_ratio
import math

class SoftSplatLinearBase(BaseInterpolator):
    def __init__(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, flow_obj=None, **args):
        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size)

        # flow to use
        self.__flow_obj = flow_obj

        # cached flow
        self.cached_flow = None
        self.cached_flow_idx = None

    def get_flow(self, image_1_idx, image_1, image_2):
        if self.cached_flow_idx != image_1_idx:
            self.cached_flow_idx = image_1_idx
            self.cached_flow = self.__flow_obj.get_flow(image_1, image_2)
        
        return self.cached_flow

    def get_interpolated_frame(self, idx):
        from .src import run
        image_1_idx, ratio = get_first_frame_idx_and_ratio(idx, self.rate_ratio)

        image_1 = self.video_stream.get_frame(image_1_idx)
        image_2 = self.video_stream.get_frame(image_1_idx + 1)

        flow = self.get_flow(image_1_idx, image_1, image_2)
        
        output = run.estimate(image_1, image_2, flow, ratio)

        return output

class SoftSplatLinearDefault(SoftSplatLinearBase):
    def __init__(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
        flow_obj = FlowsDictionary['LiteFlowNet-Default']()

        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size, flow_obj)


    def __str__(self):
        return 'SoftSplat-Linear-Default'

class SoftSplatLinearKitti(SoftSplatLinearBase):
    def __init__(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
        flow_obj = FlowsDictionary['LiteFlowNet-KITTI']()

        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size, flow_obj)

    def __str__(self):
        return 'SoftSplat-Linear-KITTI'

class SoftSplatLinearSintel(SoftSplatLinearBase):
    def __init__(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
        flow_obj = FlowsDictionary['LiteFlowNet-SINTEL']()

        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size, flow_obj)


    def __str__(self):
        return 'SoftSplat-Linear-Sintel'


    
class SoftSplatMidFrameBase(MidFrameBaseInterpolator):
    def __init__(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, flow_obj=None, **args):
        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size)

        # flow to use
        self.__flow_obj = flow_obj


    def get_middle_frame(self, image_1, image_2):
        from .src import run
        flow = self.__flow_obj.get_flow(image_1, image_2)
        
        output = run.estimate(image_1, image_2, flow)

        return output

    
class SoftSplatMidFrameDefault(SoftSplatMidFrameBase):
    def __init__(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
        flow_obj = FlowsDictionary['LiteFlowNet-Default']()

        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size, flow_obj)

    def __str__(self):
        return 'SoftSplat-MidFrame-Default'

class SoftSplatMidFrameKitti(SoftSplatMidFrameBase):
    def __init__(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
        flow_obj = FlowsDictionary['LiteFlowNet-KITTI']()

        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size, flow_obj)

    def __str__(self):
        return 'SoftSplat-MidFrame-KITTI'

class SoftSplatMidFrameSintel(SoftSplatMidFrameBase):
    def __init__(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
        flow_obj = FlowsDictionary['LiteFlowNet-SINTEL']()

        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size, flow_obj)

    def __str__(self):
        return 'SoftSplat-MidFrame-Sintel'


    
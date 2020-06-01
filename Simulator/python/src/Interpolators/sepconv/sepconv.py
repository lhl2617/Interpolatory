from ..base import MidFrameBaseInterpolator
from ...util import is_power_of_two
import math

class SepConv(MidFrameBaseInterpolator):
    def __init__(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
        self.model = 'lf'

        if 'model' in args:
            self.model = args['model']

        from .src import run
        run.arguments_strModel = self.model
        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size)

    def __str__(self):
        return f'SepConv - {self.model}'

    def get_middle_frame(self, image_1, image_2):
        import numpy
        import torch
        from .src import run

        tenFirst = torch.FloatTensor(numpy.ascontiguousarray(numpy.array(image_1)[:, :, ::-1].transpose(2, 0, 1).astype(numpy.float32) * (1.0 / 255.0)))
        tenSecond = torch.FloatTensor(numpy.ascontiguousarray(numpy.array(image_2)[:, :, ::-1].transpose(2, 0, 1).astype(numpy.float32) * (1.0 / 255.0)))

        tenOutput = run.estimate(tenFirst, tenSecond)

        out_frame = (tenOutput.clamp(0.0, 1.0).numpy().transpose(1, 2, 0)[:, :, ::-1] * 255.0).astype(numpy.uint8)

        return out_frame

    

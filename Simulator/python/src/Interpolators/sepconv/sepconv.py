from ..base import BaseInterpolator

class SepConvBase(BaseInterpolator):
    def set_model_arg(self):
        raise NotImplementedError(
            'To be implemented by SepConv L1 and Lf classes')

    def get_benchmark_frame(self, image_1, image_2):
        raise NotImplementedError(
            'To be implemented by SepConv L1 and Lf classes')

    def get_sepconv_frame(self, image_1, image_2):
        import numpy
        import torch
        from .src import run

        tenFirst = torch.FloatTensor(numpy.ascontiguousarray(numpy.array(image_1)[:, :, ::-1].transpose(2, 0, 1).astype(numpy.float32) * (1.0 / 255.0)))
        tenSecond = torch.FloatTensor(numpy.ascontiguousarray(numpy.array(image_2)[:, :, ::-1].transpose(2, 0, 1).astype(numpy.float32) * (1.0 / 255.0)))

        tenOutput = run.estimate(tenFirst, tenSecond)

        out_frame = (tenOutput.clamp(0.0, 1.0).numpy().transpose(1, 2, 0)[:, :, ::-1] * 255.0).astype(numpy.uint8)

        return out_frame


    def get_interpolated_frame(self, idx):
        raise NotImplementedError('Not implemented for limited methods')


class SepConvL1(SepConvBase):
    def set_model_arg(self):
        from .src import run
        run.arguments_strModel = 'l1'

    def get_benchmark_frame(self, image1, image2):
        self.set_model_arg()
        return self.get_sepconv_frame(image1, image2)

    def __str__(self):
        return 'SepConv - L1'


class SepConvLf(SepConvBase):
    def set_model_arg(self):
        from .src import run
        run.arguments_strModel = 'lf'

    def get_benchmark_frame(self, image1, image2):
        self.set_model_arg()
        return self.get_sepconv_frame(image1, image2)

    def __str__(self):
        return 'SepConv - Lf'



    

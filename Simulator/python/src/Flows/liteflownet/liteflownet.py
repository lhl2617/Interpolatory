
##########################################################

# if __name__ == '__main__':
# 	tenFirst = torch.FloatTensor(numpy.ascontiguousarray(numpy.array(PIL.Image.open(arguments_strFirst))[:, :, ::-1].transpose(2, 0, 1).astype(numpy.float32) * (1.0 / 255.0)))
# 	tenSecond = torch.FloatTensor(numpy.ascontiguousarray(numpy.array(PIL.Image.open(arguments_strSecond))[:, :, ::-1].transpose(2, 0, 1).astype(numpy.float32) * (1.0 / 255.0)))

# 	tenOutput = estimate(tenFirst, tenSecond)

# 	objOutput = open(arguments_strOut, 'wb')

# 	numpy.array([ 80, 73, 69, 72 ], numpy.uint8).tofile(objOutput)
# 	numpy.array([ tenOutput.shape[2], tenOutput.shape[1] ], numpy.int32).tofile(objOutput)
# 	numpy.array(tenOutput.numpy().transpose(1, 2, 0), numpy.float32).tofile(objOutput)

# 	objOutput.close()
# # end

from ..base import BaseFlow
from .src import run
import numpy

class LiteFlowNetBase(BaseFlow):
    def get_flow(self, image_1, image_2):
        import torch

        tenFirst = torch.FloatTensor(numpy.ascontiguousarray(numpy.array(image_1)[:, :, ::-1].transpose(2, 0, 1).astype(numpy.float32) * (1.0 / 255.0)))
        tenSecond = torch.FloatTensor(numpy.ascontiguousarray(numpy.array(image_2)[:, :, ::-1].transpose(2, 0, 1).astype(numpy.float32) * (1.0 / 255.0)))

        tenOutput = run.estimate(tenFirst, tenSecond)

        out = numpy.array(tenOutput.numpy().transpose(1, 2, 0), numpy.float32)

        return out

class LiteFlowNetDefault(BaseFlow):
    def __init__(self):
        run.arguments_strModel = 'default'

    def __str__(self):
        return 'LiteFlowNet - default'

class LiteFlowNetKitti(BaseFlow):
    def __init__(self):
        run.arguments_strModel = 'kitti'

    def __str__(self):
        return 'LiteFlowNet - kitti'

class LiteFlowNetSintel(BaseFlow):
    def __init__(self):
        run.arguments_strModel = 'sintel'

    def __str__(self):
        return 'LiteFlowNet - sintel'
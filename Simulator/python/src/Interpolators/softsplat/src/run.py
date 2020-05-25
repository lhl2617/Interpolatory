#!/usr/bin/env python

import torch
import numpy

from . import softsplat

##########################################################

# assert(int(str('').join(torch.__version__.split('.')[0:2])) >= 13) # requires at least pytorch version 1.3.0

##########################################################

# def read_flo(strFile):
#     with open(strFile, 'rb') as objFile:
#         strFlow = objFile.read()
#     # end

#     assert(numpy.frombuffer(strFlow, dtype=numpy.float32, count=1, offset=0) == 202021.25)

#     intWidth = numpy.frombuffer(strFlow, dtype=numpy.int32, count=1, offset=4)[0]
#     intHeight = numpy.frombuffer(strFlow, dtype=numpy.int32, count=1, offset=8)[0]

#     return numpy.frombuffer(strFlow, dtype=numpy.float32, count=intHeight * intWidth * 2, offset=12).reshape([ intHeight, intWidth, 2 ])
# # end

##########################################################

backwarp_tenGrid = {}

def backwarp(tenInput, tenFlow):
	if str(tenFlow.size()) not in backwarp_tenGrid:
		tenHorizontal = torch.linspace(-1.0, 1.0, tenFlow.shape[3]).view(1, 1, 1, tenFlow.shape[3]).expand(tenFlow.shape[0], -1, tenFlow.shape[2], -1)
		tenVertical = torch.linspace(-1.0, 1.0, tenFlow.shape[2]).view(1, 1, tenFlow.shape[2], 1).expand(tenFlow.shape[0], -1, -1, tenFlow.shape[3])

		backwarp_tenGrid[str(tenFlow.size())] = torch.cat([ tenHorizontal, tenVertical ], 1).cuda()
	# end

	tenFlow = torch.cat([ tenFlow[:, 0:1, :, :] / ((tenInput.shape[3] - 1.0) / 2.0), tenFlow[:, 1:2, :, :] / ((tenInput.shape[2] - 1.0) / 2.0) ], 1)

	return torch.nn.functional.grid_sample(input=tenInput, grid=(backwarp_tenGrid[str(tenFlow.size())] + tenFlow).permute(0, 2, 3, 1), mode='bilinear', padding_mode='zeros', align_corners=True)
# end

##########################################################

def estimate(image_1, image_2, flow, ratio=0.5):
	tenFirst = torch.FloatTensor(numpy.ascontiguousarray(numpy.array(image_1).transpose(2, 0, 1)[None, :, :, :].astype(numpy.float32) * (1.0 / 255.0))).cuda()
	tenSecond = torch.FloatTensor(numpy.ascontiguousarray(numpy.array(image_2).transpose(2, 0, 1)[None, :, :, :].astype(numpy.float32) * (1.0 / 255.0))).cuda()
	tenFlow = torch.FloatTensor(numpy.ascontiguousarray(numpy.array(flow).transpose(2, 0, 1)[None, :, :, :])).cuda()


	tenMetric = torch.nn.functional.l1_loss(input=tenFirst, target=backwarp(tenInput=tenSecond, tenFlow=tenFlow), reduction='none').mean(1, True)
	tenSoftmax = softsplat.FunctionSoftsplat(tenInput=tenFirst, tenFlow=tenFlow * ratio, tenMetric=-20.0 * tenMetric, strType='softmax') # -20.0 is a hyperparameter, called 'beta' in the paper, that could be learned using a torch.Parameter

	

	tenSoftmaxCPU = tenSoftmax.cpu()

	tenNumpy = tenSoftmaxCPU.clamp(0.0, 1.0).numpy()[0, :, :, :]


	transposed = tenNumpy.transpose(1, 2, 0)

	out_frame = (transposed * 255.0).astype(numpy.uint8)

	return out_frame
	


# tenFirst = torch.FloatTensor(numpy.ascontiguousarray(cv2.imread(filename='./images/first.png', flags=-1).transpose(2, 0, 1)[None, :, :, :].astype(numpy.float32) * (1.0 / 255.0))).cuda()
# tenSecond = torch.FloatTensor(numpy.ascontiguousarray(cv2.imread(filename='./images/second.png', flags=-1).transpose(2, 0, 1)[None, :, :, :].astype(numpy.float32) * (1.0 / 255.0))).cuda()
# tenFlow = torch.FloatTensor(numpy.ascontiguousarray(read_flo('./images/flow.flo').transpose(2, 0, 1)[None, :, :, :])).cuda()

# tenMetric = torch.nn.functional.l1_loss(input=tenFirst, target=backwarp(tenInput=tenSecond, tenFlow=tenFlow), reduction='none').mean(1, True)

# for intTime, fltTime in enumerate(numpy.linspace(0.0, 1.0, 11).tolist()):
# 	tenSummation = softsplat.FunctionSoftsplat(tenInput=tenFirst, tenFlow=tenFlow * fltTime, tenMetric=None, strType='summation')
# 	tenAverage = softsplat.FunctionSoftsplat(tenInput=tenFirst, tenFlow=tenFlow * fltTime, tenMetric=None, strType='average')
# 	tenLinear = softsplat.FunctionSoftsplat(tenInput=tenFirst, tenFlow=tenFlow * fltTime, tenMetric=(0.3 - tenMetric).clamp(0.0000001, 1.0), strType='linear') # finding a good linearly metric is difficult, and it is not invariant to translations
	# tenSoftmax = softsplat.FunctionSoftsplat(tenInput=tenFirst, tenFlow=tenFlow * fltTime, tenMetric=-20.0 * tenMetric, strType='softmax') # -20.0 is a hyperparameter, called 'beta' in the paper, that could be learned using a torch.Parameter

# 	cv2.imshow(winname='summation', mat=tenSummation[0, :, :, :].cpu().numpy().transpose(1, 2, 0))
# 	cv2.imshow(winname='average', mat=tenAverage[0, :, :, :].cpu().numpy().transpose(1, 2, 0))
# 	cv2.imshow(winname='linear', mat=tenLinear[0, :, :, :].cpu().numpy().transpose(1, 2, 0))
# 	cv2.imshow(winname='softmax', mat=tenSoftmax[0, :, :, :].cpu().numpy().transpose(1, 2, 0))
# 	cv2.waitKey(delay=0)
# # end
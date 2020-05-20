from ..base import MLBaseInterpolator
import math


class RRINInterpolator(MLBaseInterpolator):
    def __init__(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):

        from .src.model import Net
        import pathlib
        import os
        import torch

        model_path = os.path.join(pathlib.Path(
            __file__).parent, 'models', 'pretrained_model.pth.tar')

        if not (pathlib.Path(model_path).is_file()):
            readme_path = os.path.join(pathlib.Path(
                __file__).parent.parent, 'models', 'README.md')
            raise Exception(
                f'Model file ({model_path}) does not exist. Please locate README in {readme_path} for instructions to download models.')

        model = Net()
        state = torch.load(model_path)
        model.load_state_dict(state, strict=True)
        model = model.cuda()
        model.eval()

        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size)

        self.model = model

    def get_middle_frame(self, image_1, image_2):
        import torch
        import torchvision
        from torchvision import transforms
        import numpy as np

        transform = transforms.ToTensor()
        img1 = transform(image_1).unsqueeze(0).cuda()
        img2 = transform(image_2).unsqueeze(0).cuda()

        if img1.size(1) == 1:
            img1 = img1.expand(-1, 3, -1, -1)
            img2 = img2.expand(-1, 3, -1, -1)

        _, _, H, W = img1.size()
        H_, W_ = int(np.ceil(H/32)*32), int(np.ceil(W/32)*32)
        pader = torch.nn.ReplicationPad2d([0, W_-W, 0, H_-H])
        img1, img2 = pader(img1), pader(img2)

        output = self.model(img1, img2)

        output = output[0, :, 0:H, 0:W].squeeze(0).cpu()

        output = transforms.functional.to_pil_image(output)

        output = np.uint8(output)

        return output

    def __str__(self):
        return 'RRIN'

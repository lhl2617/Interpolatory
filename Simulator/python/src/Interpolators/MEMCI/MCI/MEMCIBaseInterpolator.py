from ...base import BaseInterpolator
from ..smoothing.threeXthree_mv_smoothing import smooth
from ..smoothing.median_filter import median_filter
from ..smoothing.mean_filter import mean_filter
from ..smoothing.weighted_mean_filter import weighted_mean_filter
from ..ME.full_search import get_motion_vectors as fs
from ..ME.tss import get_motion_vectors as tss
from ..ME.hbma import get_motion_vectors as hbma
import math
from ....Globals import debug_flags

print_debug = debug_flags['debug_MEMCI_args']

class MEMCIBaseInterpolator(BaseInterpolator):
    def __init__(self, target_fps,video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size,**args)
        ME_dict = {
            "fs": fs,
            "tss": tss,
            "hbma": hbma,
        }
        smoothing_dict = {
            "mean": mean_filter,
            "median": median_filter,
            "weighted": weighted_mean_filter,
            "none": None

        }
        self.MV_field_idx = -1
        self.fwr_MV_field = []
        self.bwr_MV_field = []
        self.MV_field = []
        self.block_size = 8
        self.region = 7
        self.me_mode = ME_dict["hbma"]
        # print(self.me_mode)
        self.filter_mode = smoothing_dict["none"]
        self.filter_size = 4
        self.sub_region = 1
        self.steps = 3
        self.min_block_size = 4

        self.upscale_MV = True
        # self.large_block_size = 8
        # print(args)

        if 'block_size' in args:
            arg = args['block_size']
            self.block_size = int(arg)
            if (print_debug): print(f'block_size: {arg}')
        elif print_debug: print(f'block_size: 8')

        if 'target_region' in args:
            arg = args['target_region']
            self.region = int(arg)
            if (print_debug): print(f'target_region: {arg}')
        elif print_debug: print(f'target_region: 7')

        if 'me_mode' in args:
            arg = args['me_mode']
            self.me_mode = ME_dict[arg]
            if self.me_mode==tss:
                self.region=self.steps
            if (print_debug): print(f'me_mode: {arg}')
        elif print_debug: print(f'me_mode: hbma')

        if 'filter_mode' in args:
            arg = args['filter_mode']
            self.filter_mode = smoothing_dict[arg]
            if (print_debug): print(f'filter_mode: {arg}')
        elif print_debug: print(f'filter_mode: none')

        if 'filter_size' in args:
            arg = args['filter_size']
            self.filter_size = int(arg)
            if (print_debug): print(f'filter_size: {arg}')
        elif print_debug: print(f'filter_size: 4')



        # print(self.filter_size)
        self.pad_size = 4 * self.min_block_size
        if self.me_mode == fs:
            # print('fs')
            self.ME_args = {"block_size":self.block_size, "target_region":self.region}

        elif self.me_mode == tss:
            # print('tss')
            self.ME_args = {"block_size":self.block_size, "steps":self.steps}

        elif self.me_mode == hbma:
            # print('hbma')
            self.upscale_MV = False
            self.ME_args = {"block_size":self.block_size,"win_size":self.region,
                            "sub_win_size":self.sub_region, "steps":self.steps,
                            "min_block_size":self.min_block_size,
                            "cost_str":"sad", "upscale":self.upscale_MV}
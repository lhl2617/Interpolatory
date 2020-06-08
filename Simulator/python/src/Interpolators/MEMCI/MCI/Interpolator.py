
from .Unidirectional import UniDirInterpolator
from .Bidirectional import BiDirInterpolator
from .Unidirectional_2 import UniDir2Interpolator
import math
from ....Globals import debug_flags

print_debug = debug_flags['debug_MEMCI_args']

def MEMCI (target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
    mci_mode = 'unidir'

    if 'mci_mode' in args:
        mci_mode = args['mci_mode']

    if (mci_mode == 'unidir'):
        if (print_debug): print(f'mci_mode: unidir')
        # print(args['me_mode'])
        return UniDirInterpolator(target_fps, video_in_path, video_out_path, max_out_frames, max_cache_size,**args)

    elif (mci_mode == 'bidir'):
        if (print_debug): print(f'mci_mode: bidir')
        return BiDirInterpolator(target_fps, video_in_path, video_out_path, max_out_frames, max_cache_size,**args)

    elif (mci_mode == 'unidir2'):
        # no smoothing in unidir2
        args['filter_mode'] = 'none'
        if (print_debug): print(f'mci_mode: unidir2')
        return UniDir2Interpolator(target_fps, video_in_path, video_out_path, max_out_frames, max_cache_size,**args)

    else:
        raise Exception(f'Unknown mci_mode: {mci_mode}')

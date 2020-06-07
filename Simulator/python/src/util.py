import sys
import numpy as np
import math
from fractions import Fraction
from decimal import Decimal
from numba import njit, float32, int32, boolean, types

progress_file_path = None

def eprint(s):
    print(s, file=sys.stderr)

def sToMMSS(s):
    mm = int(s / 60)
    ss = str(int(s % 60)).rjust(2, '0')
    return f'{mm}:{ss}'

    
'''
estimate time left
'''
def getETA(elapsed_seconds, processed_frames, all_frames):
    remaining_frames = all_frames - processed_frames

    eta_seconds = 0 if processed_frames == 0 else int(float(elapsed_seconds) / processed_frames * remaining_frames)
    return sToMMSS(eta_seconds)

# signal progress by writing into progress_file
def signal_progress(s):
    global progress_file_path
    if (not (progress_file_path is None)):
        with open(progress_file_path, 'w') as progress_file:
            progress_file.write(s)
            progress_file.flush()

'''
blends frames
'''
def blend_frames(frames, weights=None):
    return np.average(frames, axis=0, weights=weights).astype(np.uint8, copy=False)

def is_power_of_two(n):
    if (n == 0):
        return True 
    return (math.ceil(np.log2(n))) == math.floor(np.log2(n))



@njit(types.Tuple((int32, float32))(int32, float32))
def get_first_frame_idx_and_ratio(idx, rate_ratio):
    '''
    used in linear, rrin and other ML methods that support multiplying the flow
    

    given a rate_ratio and idx, figure out what the first_frame_idx (last possible frame that is before the idx time)
    and the ratio of time between this frame and the next
    '''
    ret_idx = math.floor(idx / rate_ratio)
    ratio = 1. - (idx / rate_ratio - ret_idx)
    return ret_idx, ratio    
    


# deconstruct the string into a dict
def deconstruct_settings(s):
    ret = {}
    pairs = s.split('.')
    for pair in pairs:
        unsplit = pair.split('=')
        if len(unsplit) != 2:
            eprint(f'Ignoring {pair}, malformed input')
            continue
    
        [key, val] = unsplit
        if len(key) > 0 and len(val) > 0:
            ret[key] = val
        else:
            eprint(f'Ignoring {key} {val}, malformed input')

    return ret

# manage <interpolation-mode>[:<settings>]
def deconstruct_interpolation_mode_and_settings(s):
    pair = s.split(':')
    if len(pair) == 1:
        return pair[0], {}
    elif len(pair) == 2:
        settings = deconstruct_settings(pair[1])
        return pair[0], settings
    else:
        eprint(f'Invalid interpolation-mode and settings config: {s}')
        exit(1)
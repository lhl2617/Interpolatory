import sys
import numpy as np
import math
from fractions import Fraction
from decimal import Decimal

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

def log2(n):
    return (math.log10(n) / math.log10(2))

def is_power_of_two(n):
    return (math.ceil(log2(n))) == math.floor(log2(n))


def get_first_frame_idx_and_ratio(idx, rate_ratio):
    '''
    used in linear, rrin and other ML methods that support multiplying the flow
    

    given a rate_ratio and idx, figure out what the first_frame_idx (last possible frame that is before the idx time)
    and the ratio of time between this frame and the next
    '''
    
    # this period is the number of frame in the targetRate
    # before a cycle occurs (e.g. in the 24->60 case it occurs between B &
    # C at period = 5
    frac = Fraction(Decimal(rate_ratio))
    period = frac.numerator


    # which targetFrame is this after a period
    offset = math.floor(idx % period)


    # a key frame is a source frame that matches in time, this key frame
    # is the latest possible source frame
    key_frame_idx = math.floor(idx / period) * period

    rate_ratios_from_key_frame = math.floor(offset / rate_ratio)

    distance_from_prev_rate_ratio_point = offset - \
        (rate_ratios_from_key_frame) * rate_ratio

    frameA_idx = math.floor(
        key_frame_idx / rate_ratio + rate_ratios_from_key_frame)
        
    ratio = float(rate_ratio - distance_from_prev_rate_ratio_point) / rate_ratio

    return frameA_idx, ratio

# deconstruct the string into a dict
def deconstruct_settings(s):
    ret = {}
    pairs = s.split(',')
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
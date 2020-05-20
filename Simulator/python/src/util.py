import sys
import numpy as np
import math

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
def blend_frames(frames, weights):
    return np.average(frames, axis=0, weights=weights).astype(np.uint8, copy=False)

def log2(n):
    return (math.log10(n) / math.log10(2))

def is_power_of_two(n):
    return (math.ceil(log2(n))) == math.floor(log2(n))
import sys

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


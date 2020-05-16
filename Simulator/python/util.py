import sys

def eprint(s):
    print(s, file=sys.stderr)

def sToMMSS(s):
    mm = int(s / 60)
    ss = str(int(s % 60)).rjust(2, '0')
    return f'{mm}:{ss}'
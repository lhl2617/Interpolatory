from sys import argv
import math

def write_bandwidth(r, c):
    return 72 * r * c

def read_bandwidth(r, c):
    return 180 * r * c

def calc(**args):
    r = int(args.get('r', 1080))
    c = int(args.get('c', 1920))

    res = {}
    res['Write (MB/s)'] = write_bandwidth(r, c)/(1024**2)
    res['Read (MB/s)'] = read_bandwidth(r, c)/(1024**2)
    res['Cache (MB)'] = 0

    # round to 2dp
    for key, val in res.items():
        res[key] = round(val, 2)

    return res
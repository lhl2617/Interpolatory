from sys import argv
import math

def window_size(b, s):
    total = 0
    for i in range(s):
        total += 2 ** i
    total *= 2
    total += b
    return total

def write_bandwidth(r, c):
    return 216 * r * c

def read_bandwidth(r, c):
    return 300 * r * c

def cach_required(c, b, w):
    return 2 * c * (4 * b + 3 * (2 * w + 5))

def calc(**args):
    b = int(args.get('b', 8))
    r = int(args.get('r', 1080))
    c = int(args.get('c', 1920))
    steps = int(args.get('steps', 3))
    w = window_size(b, steps)

    res = {}
    res['Write (MB/s)'] = write_bandwidth(r, c)/(1024**2)
    res['Read (MB/s)'] = read_bandwidth(r, c)/(1024**2)
    res['Cache (MB)'] = cach_required(c, b, w)/(1024**2)

    # round to 2dp
    for key, val in res.items():
        res[key] = round(val, 2)

    return res

# b = int(argv[1])
# r = int(argv[2])
# c = int(argv[3])
# w = int(argv[4])

# print('Write:', write_bandwidth(r, c)/(1024**2), 'MB/s')
# print('Read:', read_bandwidth(r, c)/(1024**2), 'MB/s')
# print('Cache:', cach_required(c, b, w)/(1024**2), 'MB')
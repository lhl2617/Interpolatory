from sys import argv
import math

def write_bandwidth(r, c):
    return 216 * r * c

def read_bandwidth(r, c):
    return 252 * r * c

def cach_required(c, b, w):
    return 6 * c * (b + 2 * w + 5)

def calc(**args):
    b = int(args.get('b', 8))
    r = int(args.get('r', 1080))
    c = int(args.get('c', 1920))
    w = int(args.get('w', 22))


    res = {}
    res['Write'] = f'{write_bandwidth(r, c)/(1024**2)}MB/s'
    res['Read'] = f'{read_bandwidth(r, c)/(1024**2)}MB/s'
    res['Cache'] = f'{cach_required(c, b, w)/(1024**2)}MB'

# b = int(argv[1])
# r = int(argv[2])
# c = int(argv[3])
# w = int(argv[4])

# print('Write:', write_bandwidth(r, c)/(1024**2), 'MB/s')
# print('Read:', read_bandwidth(r, c)/(1024**2), 'MB/s')
# print('Cache:', cach_required(c, b, w)/(1024**2), 'MB')
import math
import sys

def a(s, w, i):
    total = 2 ** (s-i) * w
    for n in range(1, s-i+1):
        total += 2 ** n
    return total

def pad(b_max, b_min):
    total = 0
    for n in range(1, int(math.log(b_max//b_min, 2))+1):
        total += 2 ** n
    return total

def num1(b_min, c):
    return 6 * b_min * c

def num2(s, b_max, c):
    total = 0
    for i in range(1, s+1):
        total += 2 * b_max * c/(2 ** i)
    return total

def win_cache(s, w, c, b_max, b_min):
    total = 0
    for i in range(0, s+1):
        total += a(s, w, i) * c/(2 ** i)
    total += pad(b_max, b_min) * c
    return total

def write_cache(s, w, b_max, b_min, c):
    return 6 * (a(s, w, 0) + pad(b_max, b_min) + 5) * c

def w_h_s_cache(s, w, b_max, b_min, c):
    return 4 * (a(s, w, 0) + pad(b_max, b_min)) * c

def vec_cache(s, c, b_max):
    total = 0
    for i in range(0, s+1):
        total += 4 * c/(2 ** i + b_max)
    return total

def cache_required(b_max, b_min, c, w, s):
    return num1(b_min, c) + num2(s, b_max, c) + win_cache(s, w, c, b_max, b_min) + write_cache(s, w, b_max, b_min, c) + w_h_s_cache(s, w, b_max, b_min, c) + vec_cache(s, c, b_max)

def write_bandwidth(r, c, s):
    total = 9 * r * c
    for i in range(1, s+1):
        total += r * c / (2 ** i)
    total *= 24
    return total

def read_bandwidth(r, c, s):
    total = 0
    for i in range(0, s+1):
        total += r * c / (2 ** i)
    total *= 48
    total += 228 * r * c
    return total

def calc(**args):
    r = int(args.get('r', 1080))
    c = int(args.get('c', 1920))
    w = int(args.get('w', 22)) 
    s = int(args.get('s', 2))
    b_max = int(args.get('b_max', 8)) 
    b_min = int(args.get('b_min', 4))

    res = {}
    res['Write'] = f'{write_bandwidth(r, c, s)/(1024**2)}MB/s'
    res['Read'] = f'{read_bandwidth(r, c, s)/(1024**2)}MB/s'
    res['Cache'] = f'{cache_required(b_max, b_min, c, w, s)/(1024**2)}MB'
    
    return res

# b_max = int(sys.argv[1])
# b_min = int(sys.argv[2])
# r = int(sys.argv[3])
# c = int(sys.argv[4])
# w = int(sys.argv[5])
# s = int(sys.argv[6])

# print('write:',write_bandwidth(r, c, s)/(1024**2), 'MB')
# print('read:', read_bandwidth(r, c, s)/(1024**2), 'MB')
# print('cache:', cache_required(b_max, b_min, c, w, s)/(1024**2), 'MB')
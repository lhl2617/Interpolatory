from sys import argv
import math

def write_bandwidth(r, c):
    return 216 * r * c

def read_bandwidth(r, c):
    return 300 * r * c

def cach_required(c, b, w):
    return 2 * c * (4 * b + 3 * (2 * w + 5))

b = int(argv[1])
r = int(argv[2])
c = int(argv[3])
w = int(argv[4])

print('Write:', write_bandwidth(r, c)/(1024**2), 'MB/s')
print('Read:', read_bandwidth(r, c)/(1024**2), 'MB/s')
print('Cache:', cach_required(c, b, w)/(1024**2), 'MB')
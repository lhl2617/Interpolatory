from .Interpolators import linear, oversample, nearest
from .Interpolators.sepconv import sepconv
from .Interpolators.rrin import rrin

# supports all features
InterpolatorDictionary = {
    'Nearest': nearest.NearestInterpolator,
    'Oversample': oversample.OversampleInterpolator,
    'Linear': linear.LinearInterpolator,
    'SepConvL1-CUDA': sepconv.SepConvL1,
    'SepConvLf-CUDA': sepconv.SepConvLf,
    'RRIN-CUDA': rrin.RRINInterpolator
}

# supports only benchmarking and middle frame generation
# this should contain all interpolators
LimitedInterpolatorDictionary = {
}

# add into all
for (a, b) in InterpolatorDictionary.items():
    LimitedInterpolatorDictionary[a] = b





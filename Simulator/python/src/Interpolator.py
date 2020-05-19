from .Interpolators import linear, oversample, nearest
from .Interpolators.sepconv import sepconv

# supports all features
InterpolatorDictionary = {
    'Nearest': nearest.NearestInterpolator,
    'Oversample': oversample.OversampleInterpolator,
    'Linear': linear.LinearInterpolator
}

# supports only benchmarking and middle frame generation
# this should contain all interpolators
LimitedInterpolatorDictionary = {
    'SepConvL1-CUDA': sepconv.SepConvL1,
    'SepConvLf-CUDA': sepconv.SepConvLf
}

# add into all
for (a, b) in InterpolatorDictionary.items():
    LimitedInterpolatorDictionary[a] = b





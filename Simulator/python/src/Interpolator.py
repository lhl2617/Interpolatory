from .Interpolators import linear, oversample, nearest, blur, speed
from .Interpolators.sepconv import sepconv
from .Interpolators.rrin import rrin

# supports all features
InterpolatorDictionary = {
    'Nearest': nearest.NearestInterpolator,
    'Oversample': oversample.OversampleInterpolator,
    'Linear': linear.LinearInterpolator,
    'Blur': blur.BlurInterpolator,
    'Speed': speed.SpeedInterpolator,
    'SepConvL1-CUDA': sepconv.SepConvL1,
    'SepConvLf-CUDA': sepconv.SepConvLf,
    'RRIN-CUDA': rrin.RRINInterpolator,

}

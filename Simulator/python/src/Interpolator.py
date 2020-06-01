from .Interpolators import nearest, blur, speed, oversample, linear
from .Interpolators.sepconv import sepconv
from .Interpolators.rrin import rrin
# from .Interpolators.MEMCI import Interpolator
# supports all features
InterpolatorDictionary = {
    'Nearest': nearest.NearestInterpolator,
    'Oversample': oversample.OversampleInterpolator,
    'Linear': linear.LinearInterpolator,
    'Blur': blur.BlurInterpolator,
    'Speed': speed.SpeedInterpolator,
    'SepConvL1-CUDA': sepconv.SepConvL1,
    'SepConvLf-CUDA': sepconv.SepConvLf,
    'RRIN-MidFrame-CUDA': rrin.RRINMidFrameInterpolator,
    'RRIN-Linear-CUDA': rrin.RRINLinearInterpolator,
    # 'Unidirectional':Interpolator.MEMCIInterpolator,
    # 'Bidirectional':Interpolator.Bi,
}

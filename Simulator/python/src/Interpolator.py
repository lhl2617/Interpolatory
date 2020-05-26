from .Interpolators import nearest, blur, speed, oversample, linear
from .Interpolators.sepconv import sepconv
from .Interpolators.rrin import rrin
from .Interpolators.softsplat import softsplat
from .Interpolators.MEMCI import Interpolator, Unidirectional_2

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
    'SoftSplat-Linear-Default': softsplat.SoftSplatLinearDefault,
    'SoftSplat-Linear-KITTI': softsplat.SoftSplatLinearKitti,
    'SoftSplat-Linear-Sintel': softsplat.SoftSplatLinearSintel,
    'SoftSplat-MidFrame-Default': softsplat.SoftSplatMidFrameDefault,
    'SoftSplat-MidFrame-KITTI': softsplat.SoftSplatMidFrameKitti,
    'SoftSplat-MidFrame-Sintel': softsplat.SoftSplatMidFrameSintel,
    'Unidirectional':Interpolator.MEMCIInterpolator,
    'Bidirectional':Interpolator.Bi,
    'Unidirectional_2':Unidirectional_2.Uni_2
}

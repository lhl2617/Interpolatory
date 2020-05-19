from .Interpolators import linear, oversample, nearest

InterpolatorDictionary = {
    'nearest': nearest.NearestInterpolator,
    'oversample': oversample.OversampleInterpolator,
    'linear': linear.LinearInterpolator
}


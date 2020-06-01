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
    'SepConv-CUDA': sepconv.SepConv,
    'RRIN-CUDA': rrin.RRIN
    # 'Unidirectional':Interpolator.MEMCIInterpolator,
    # 'Bidirectional':Interpolator.Bi,
}


InterpolatorDocs = {
    "Nearest": {
        "description": "Known as drop/repeat. Nearest frame in point of time is used"
    },
    "Oversample": {
        "description": "Similar to nearest except frames at boundaries are blended (oversampled)"
    },
    "Linear": {
        "description": "Bilinear interpolation in which new frames are created by blending frames by their weights w.r.t. time"
    },
    "Blur": {
        "description": "Downconverts frame rate and blends frames, supports only downconversion by 2 to the n where n is an integer"
    },
    "Speed": {
        "description": "Converts frame rate by simply changing the speed of the video. No frame is created nor dropped."
    },
    "SepConv-CUDA": {
        "description": "SepConv kernel-based method. Requires CUDA dependencies. Supports only upconversion by a factor of 2 or if the factor has denominator 2 (e.g. 2.5 = 5/2). For the latter case, upconversion is done at a doubled factor and a pair of frames are blended to create one output frame.",
        "options": {
            "model": {
                "type": "enum",
                "description": "Specify which model to use",
                "default": "L1",
                "enum": [
                    "l1",
                    "lf"
                ],
                "enumDescriptions": [
                    "Using the L1 model (benchmark optimised)",
                    "Using the Lf model (qualitative results optimised)"
                ]
            }
        }
    },
    "RRIN-CUDA": {
        "description": "Residue Refinement method. Requires CUDA dependencies.",
        "options": {
            "flow_usage_method": {
                "type": "enum",
                "description": "How the flow between two images is used.",
                "default": "linear",
                "enum": [
                    "midframe",
                    "linear"
                ],
                "enumDescriptions": [
                    "Uses only midpoint of flow to interpolate output flow. Supports only upconversion by a factor of 2 or if the factor has denominator 2 (e.g. 2.5 = 5/2). For the latter case, upconversion is done at a doubled factor and a pair of frames are blended to create one output frame.",
                    "Uses bilinear interpolation based on the flow between two consecutive original frames."
                ]
            }
        }
    },
    "MEMCI": {
        "description": "Motion Estimation & Motion Compensated Interpolation method.",
        "options": {
            "ME_Method": {
                "type": "enum",
                "description": "Which Motion Estimation method to use.",
                "default": "hbma",
                "enum": [
                    "hbma",
                    "fs",
                    "tss"
                ],
                "enumDescriptions": [
                    "Hierarchical Block Matching Algorithm",
                    "Full Search",
                    "Three Step Search"
                ]
            },
            "block_size": {
                "type": "number",
                "default": 16,
                "description": "Block size (positive integer) used by ME"
            },
            "MCI_Method": {
                "type": "enum",
                "description": "Which Motion Compensated Interpolation method to use.",
                "default": "bidir",
                "enum": [
                    "unidir",
                    "bidir",
                    "uidir2"
                ],
                "enumDescriptions": [
                    "Unidirectional Method",
                    "Bidirectional Method",
                    "Improved Unidirectional Method"
                ]
            },
            "filter_method": {
                "type": "enum",
                "description": "Which filtering method to use.",
                "default": "weighted_mean",
                "enum": [
                    "mean",
                    "median",
                    "weighted_mean"
                ],
                "enumDescriptions": [
                    "Mean",
                    "Median",
                    "Weighted Mean"
                ]
            },
            "filter_size": {
                "type": "number",
                "default": 4,
                "description": "Filter size (positive integer) used by MCI filter method"
            }
        }
    }
}

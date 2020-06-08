# from .Interpolators.MEMCI.MCI import Interpolator, Unidirectional_2
from .Interpolators.sepconv import sepconv
from .Interpolators.rrin import rrin
from .Interpolators import nearest, blur, speed, oversample, linear
from .Interpolators.MEMCI.MCI import Interpolator
# supports all features
InterpolatorDictionary = {
    'Nearest': nearest.NearestInterpolator,
    'Oversample': oversample.OversampleInterpolator,
    'Linear': linear.LinearInterpolator,
    'Blur': blur.BlurInterpolator,
    'Speed': speed.SpeedInterpolator,
    'SepConv-CUDA': sepconv.SepConv,
    'RRIN-CUDA': rrin.RRIN,
    'MEMCI': Interpolator.MEMCI
    # 'Unidirectional':Interpolator.MEMCIInterpolator,
    # 'Bidirectional':Interpolator.Bi,
}


InterpolatorDocs = {
    "Nearest": {
        "name": "Nearest",
        "description": "Known as drop/repeat. Nearest frame in point of time is used",
        "modes": {
            "-i": True, # interpolate
            "-b": True, # benchmark
            "-t": True, # middle frame
            "-e": False # estimate hardware
        }
    },
    "Oversample": {
        "name": "Oversample",
        "description": "Similar to nearest except frames at boundaries are blended (oversampled)",
        "modes": {
            "-i": True, # interpolate
            "-b": True, # benchmark
            "-t": True, # middle frame
            "-e": False # estimate hardware
        }
    },
    "Linear": {
        "name": "Linear",
        "description": "Bilinear interpolation in which new frames are created by blending frames by their weights w.r.t. time",
        "modes": {
            "-i": True, # interpolate
            "-b": True, # benchmark
            "-t": True, # middle frame
            "-e": True # estimate hardware
        }
    },
    "Blur": {
        "name": "Blur",
        "description": "Downconverts frame rate and blends frames, supports only downconversion by 2 to the n where n is an integer",
        "modes": {
            "-i": True, # interpolate
            "-b": False, # benchmark
            "-t": False, # middle frame
            "-e": False # estimate hardware
        }
    },
    "Speed": {
        "name": "Speed",
        "description": "Converts frame rate by simply changing the speed of the video. No frame is created nor dropped.",
        "modes": {
            "-i": True, # interpolate
            "-b": False, # benchmark
            "-t": False, # middle frame
            "-e": False # estimate hardware
        }
    },
    "MEMCI": {
        "name": "MEMCI",
        "description": "Motion Estimation & Motion Compensated Interpolation method.",
        "modes": {
            "-i": True, # interpolate
            "-b": True, # benchmark
            "-t": True, # middle frame
            "-e": True # estimate hardware
        },
        "options": {
            "me_mode": {
                "type": "enum",
                "description": "Which Motion Estimation method to use.",
                "value": "hbma",
                "enum": [
                    "hbma",
                    "fs",
                    "tss",
                ],
                "enumDescriptions": [
                    "Hierarchical Block Matching Algorithm",
                    "Full Search",
                    "Three Step Search",
                ]
            },
            "block_size": {
                "type": "number",
                "value": 8,
                "description": "Block size (positive integer) used by ME"
            },
            "target_region": {
                "type": "number",
                "value": 3,
                "description": "The distance in pixels (positive integer) that the algorithm searches for motion"
            },
            "mci_mode": {
                "type": "enum",
                "description": "Which Motion Compensated Interpolation method to use.",
                "value": "unidir",
                "enum": [
                    "unidir",
                    "bidir",
                    "unidir2"
                ],
                "enumDescriptions": [
                    "Unidirectional Method",
                    "Bidirectional Method",
                    "Improved Unidirectional Method"
                ]
            },
            "filter_mode": {
                "type": "enum",
                "description": "Which filtering method to use.",
                "value": "weighted_mean",
                "enum": [
                    "mean",
                    "median",
                    "weighted"
                ],
                "enumDescriptions": [
                    "Mean",
                    "Median",
                    "Weighted Mean"
                ]
            },
            "filter_size": {
                "type": "number",
                "value": 5,
                "description": "Filter size (positive integer) used by MCI filter method"
            }
        }
    },
    "SepConv-CUDA": {
        "name": "SepConv-CUDA",
        "description": "SepConv kernel-based method. Requires CUDA dependencies. Supports only upconversion by a factor of 2 or if the factor has denominator 2 (e.g. 2.5 = 5/2). For the latter case, upconversion is done at a doubled factor and a pair of frames are blended to create one output frame.",
        "modes": {
            "-i": True, # interpolate
            "-b": True, # benchmark
            "-t": True, # middle frame
            "-e": False # estimate hardware
        },
        "options": {
            "model": {
                "type": "enum",
                "description": "Specify which model to use",
                "value": "l1",
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
        "name": "RRIN-CUDA",
        "description": "Residue Refinement method. Requires CUDA dependencies.",
        "modes": {
            "-i": True, # interpolate
            "-b": True, # benchmark
            "-t": True, # middle frame
            "-e": False # estimate hardware
        },
        "options": {
            "flow_usage_method": {
                "type": "enum",
                "description": "How the flow between two images is used.",
                "value": "linear",
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
    }
}

def checkValidMode(interpolator_str, mode_flag):
    if not interpolator_str in InterpolatorDocs:
        raise Exception(f'Invalid interpolator name: `{interpolator_str}`')
    interpolator_modes = InterpolatorDocs[interpolator_str]['modes']
    if not interpolator_modes[mode_flag]:
        raise Exception (f'Unsupported mode `{mode_flag}` for `{interpolator_str}`')

def getIDocs():
    print('# Interpolator Documentation')

    modeOptionMap = {
        '-i': '-i (Video Interpolation)',
        '-b': '-b (Benchmarking)',
        '-t': '-t (Getting middle frame)',
        '-e': '-e (Get hardware estimates)'
    }

    def getOptions(iDocOptions):
        for key, optionObj in iDocOptions.items():
            print(f'- `{key}`')
            desc = optionObj['description']
            print(f'    - {desc}')
            defaultVal = optionObj['value']
            print(f'    - Default: `{defaultVal}`')
            if optionObj['type'] == 'enum':
                print(f'    - Possible values: ')
                for i in range(len(optionObj['enum'])):
                    enumChoice = optionObj['enum'][i]
                    enumDesc = optionObj['enumDescriptions'][i]
                    print(f'        * `{enumChoice}`: {enumDesc}')

    for key, iDocObj in InterpolatorDocs.items():
        print(f'## {key}')
        name = iDocObj['name']
        desc = iDocObj['description']
        print(f'- Name: `{name}`')
        print(f'- Description: {desc}')
        print(f'### Supported modes')
        for mode, enabled in iDocObj['modes'].items():
            print (f'{modeOptionMap[mode]}: {enabled}')   
        if 'options' in iDocObj:
            print(f'### Options')
            getOptions(iDocObj['options'])

        
        print('')
    


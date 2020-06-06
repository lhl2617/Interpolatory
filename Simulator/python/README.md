# Interpolatory Python CLI

## Getting Started

### Prefer a GUI?
See [`../gui/README.md`](../gui/README.md).

### Requirements:
- Python 3 (tested on 3.8.2 Windows & 3.6.2 Ubuntu 18.04)
- Basic requirements: [`requirements.txt`](requirements.txt).
    - Run `python3 -m pip install requirements.txt` to install these requirements.
    - To check you meet these requirements, run `python3 main.py -dep`.
- CUDA requirements (required to run ML/CNN methods): [`cuda-requirements.txt`](cuda-requirements.txt).
    - Run `python3 -m pip install cuda-requirements.txt` to install these requirements.
    - To check you meet these requirements, run `python3 main.py -depcuda`.
    - To run ML methods, please download pretrained models, instructions can be found [here for RRIN-CUDA](src/Interpolators/rrin/models/README.md) and [here for SepConv-CUDA](src/Interpolators/sepconv/models/README.md). 
    - You will need a supported CUDA-enabled NViDIA GPU. 
    
## Usage Guide

Run `python3 main.py -h`, or see [`docs/USAGEGUIDE.md`](docs/USAGEGUIDE.md) for a usage guide.

Supported interpolation modes can be found using `python3 main.py -docs`, or see [`docs/INTERPOLATOR_DOCS.md`](docs/INTERPOLATOR_DOCS.md).


## Acknowledgments

- S. Niklaus, L. Mai, and F. Liu, “Video frame interpolation via
adaptive separable convolution,” in IEEE International Conference
on Computer Vision, 2017
    - [SepConv Implementation](https://github.com/sniklaus/sepconv-slomo)
- H. Li, Y. Yuan and Q. Wang, "Video Frame Interpolation Via Residue Refinement," ICASSP 2020 - 2020 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP), Barcelona, Spain, 2020, pp. 2613-2617, doi: 10.1109/ICASSP40776.2020.9053987
    - [RRIN Implementation](https://github.com/HopLee6/RRIN)
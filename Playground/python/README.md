# Python README

## Getting started
- `python3 -v`: check that you have Python3
- `python3 main.py`: run code
    - requirements.txt coming soon, you might need to pip3 install required libs

## Files
- `benchmark.py`
    - Run `python3 benchmark.py` to run benchmarks to get PSNR and SSIM over Middlebury dataset
- `Globals.py`
    - Global variables, also currently contains debug settings to log more/less debug info
- `Interpolator.py`
    - Contains classes with implementation of interpolation algorithm logic
- `main.py`
    - Entry point for interpolation, play around to try different interpolation algorithms
- `VideoStream.py`
    - Video representation in Python, has cache etc. to simulate hardware and to speed up running
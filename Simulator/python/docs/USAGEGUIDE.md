# Usage Guide

### `python3 main.py -h`
- Get this help.

### `python3 main.py -ver`
- Get version

### `python3 main.py -dep`
- Check whether normal requirements are met

### `python3 main.py -depcuda`
- Check whether CUDA dependencies are metGet this help. 

### `python3 main.py -doc`
- List all supported interpolation modes and their CLI usage guide

### `python3 main.py -doc-estimator`
- List all supported interpolation estimator modes and their CLI usage guide

### `python3 main.py -mv <video-path>`
- Load a video and print metadata to stdout. Used to check if a video is supported. If not supported, will return non-zero value.

### `python3 main.py -mi <video-path>`
- Load an image and print height, width, and colour dimensions to stdout. Used to check if an image is supported. If not supported, will return non-zero value

### `python3 main.py -i <input-video-path> -m <interpolation-mode>:[<settings>] -f <output-frame-rate> -o <output-file-path>`
- Get in an input video source from `<input-video-path>` and, using `<interpolation-mode>` mode, interpolate to `<output-frame-rate>` fps and save to `<output-file-path>`
- Extra configuration settings can be set in `<settings>` using dot separated key-value pairs, e.g. for MEMCI, `"MEMCI:block_size=32.filter_size=8"`
- See interpolation mode usage guides in `python3 main.py -doc`

### `python3 main.py -b <interpolation-mode>[:<settings>] [<output-folder>]`
- Run Middlebury benchmark to get results based on an `<interpolation-mode>`
- If provided, outputs interpolated images to `<output-folder>`
- See interpolation mode usage guides in `python3 main.py -doc`

### `python3 main.py -t <interpolation-mode>[:<settings>] -f <frame1> <frame2> -o <output-file-path> [<ground-truth-path>]`
- Using `<interpolation mode>`, get the interpolated midpoint frame between `<frame1>` and `<frame2>`, saving the output to `<output-file-path>`
- If `[<ground-truth-path>]` is provided, metrics (PSNR & SSIM) are returned
- Extra configuration settings can be set in `<settings>` using dot separated key-value pairs, e.g. for MEMCI, `"MEMCI:block_size=32.filter_size=8"`
- See interpolation mode usage guides in `python3 main.py -doc`

### `python3 main.py -e <interpolation-estimator-mode>[:<settings>] 
- Estimate hardware requirements using `<interpolation-estimator-mode>`
- Extra configuration settings can be set in `<settings>` using dot separated key-value pairs, e.g. for MEMCI, `"MEMCI_unidir_fs:b=16.r=720"`
- See interpolation estimator mode usage guides in `python3 main.py -doc-estimator`
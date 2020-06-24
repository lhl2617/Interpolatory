# Linear Interpolation :

## Parameters

- `r` = number of rows of pixels in frame
- `c` = number of columns of pixels in frame

## Linear Algorithm

- Keep 2 frames in DRAM
- As frame is streamed in, if both frame slots in DRAM are filled replace oldest frame.
- Also create all interpolated frames using the frame being streamed in and the newer frame in DRAM
    - If either of the weightings for the source and target frame are 0 then do not write-back the interpolated frame (The interpolated frame, in this case, is a copy of either the source or target frame)
- Stream out scheduled frame from DRAM

## Hardware Estimation

### DRAM Writing Bandwidth:

- For each incoming frame (1/24 s):
    - Entire frame is written to DRAM:
        - 3 * `r` * `c` bytes
    - Interpolated frames are written to DRAM
        - (3 * `r` * `c`) * 2 bytes
        - For this specific frame rate conversion (24-60) every input frame produces 2 interpolated frames, all of which need to be written to DRAM
- Total :
    - 216 * `r` * `c` bytes / s


### DRAM Reading Bandwidth:

- For each incoming frame (1/24 s):
    - Previous frame is read from DRAM
        - 3 * `r` * `c` bytes
- For each outgoing frame (1/60 s):
    - Entire frame is read from DRAM
        - 3 * `r` * `c` bytes
- Total :
    - 252 * `r` * `c` bytes / s

### Required Cache Size

- None

### Example Estimations:

For:
- `r` = 1080
- `c` = 1920

Results:
- DRAM write bandwidth = 447.9 MB/s
- DRAM read bandwidth = 522.5 MB/s
- Required cache size = 0 MB

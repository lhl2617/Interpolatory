# Frame Repetition Interpolation :

## Parameters

- `r` = number of rows of pixels in frame
- `c` = number of columns of pixels in frame

## Frame Repetition Algorithm

- As frame is streamed in, store in DRAM and replace previous frame.
- When new frame is scheduled to be streamed out, stream out frame in DRAM

## Hardware Estimation

### DRAM Writing Bandwidth:

- For each incoming frame (1/24 s):
    - Entire frame is written to DRAM:
        - 3 * `r` * `c` bytes
- Total :
    - 72 * `r` * `c` bytes / s

### DRAM Reading Bandwidth:

- For each outgoing frame (1/60 s):
    - Entire frame is read from DRAM
        - 3 * `r` * `c` bytes
- Total :
    - 180 * `r` * `c` bytes / s

### Required Cache Size

- None
    - Since you do read the same frame from DRAM multiple times you could potentially cache the frame, however this may cause an unfeasible resource footprint on the board.


### Example Estimations:

For:
- `r` = 1080
- `c` = 1920

Results:
- DRAM write bandwidth = 149.3 MB/s
- DRAM read bandwidth = 373.2 MB/s
- Required cache size = 0 MB
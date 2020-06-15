# Full Search ME and Bidirectional MCI:

## Parameters:

- `b` = size of single axis of block in pixels
- `r` = number of rows of pixels in frame
- `c` = number of columns of pixels in frame
- `w` = size of single axis of search window in pixels

## Full Search:

- For each block in first image (`source block`):
    - Calculate SAD of `source block` with blocks of matching size in a window in the second image
        - For each block in the window in the second image (`target block`):
            - Calculate SAD of `source block` and `target block` and note corresponding vector
    - Take the vector corresponding to the lowest SAD and record in output with SAD (for occlusion in MCI) (in cases where there are multiple lowest SADs, precedence should be given to the smallest vector)
- Return block-wise motion vector field

## Bidirectional Interpolation:

- Calculate forward and backward motion vectors using previous algorithm
    - Swap frames to get backward motion vectors
- Create interpolated frame
- Create `r` * `c` SAD table
- Create `r` * `c` hole table
- For each block in the source frame:
    - Find new coordinates of block in interpolated frame (by following forward vector)
    - Any pixels that are already written, compare SAD with table value and overwrite if lower
    - Fill all other pixels
    - Record them as being filled in the hole table
    - Record SAD in SAD table
- For each block in the target frame:
    - Find new coordinates of block in interpolated frame (by following backward vector)
    - Any pixels that are already written, compare SAD with table value and overwrite if lower
    - Fill all other pixels
    - Record them as being filled in the hole table
    - Record SAD in SAD table
- For each pixel in interpolated frame:
    - If hole table says pixel is a hole:
        - Apply median filter over hole

## Full Integrated System:

To save on resources, the Y channel of YCbCr images are used for the motion estimation, as it has only a small effect on performance.

When describing cache, sizes are given as (rows, columns).

Images are assumed to be YCbCr. If not, a conversion is applied as it is streamed in.

The following stage is designed to store the incoming frame in a block wise format, as apposed to raster order.

- Create (2 * `b`, `c`) * 3 bytes cache
- As the first frame streams in, place the pixels into the cache
- When `b` rows have been streamed in, start writing the cache to DRAM in a block wise fashion
    - All 3 channels are written to DRAM as separate 1 channel images
    - Blocks are flattened and then written in contiguously
    - Left to right
    - Stream frame into the other `b` rows while writing
    - Repeat until full image in DRAM and stored block wise

After first frame, the following stages happen in a loop with each incoming frame (target frame):

- Create (`w`, `c`) * 1 byte cache (called `source_win_cache`)
    - This cache will be used to search the source frame for the motion vectors
- Create (`w` + `b`, `c`) * 1 byte cache (called `target_win_cache`)
    - This cache will be used to search the target frame for the motion vectors
    - The height is `w`+`b` so that the first row of windows can be searched while the values needed for the next row are streamed in
- Create (`w` + 5, `c`) * 3 bytes cache (called `write_cache`)
    - This cache is to store the interpolated frame as it's being written to save bandwidth
    - As 2 frames are interpolated between each input frame, 2 of these caches are required
    - Set top 5 rows to 0
    - Start addressing after top 5 rows (top 5 rows are only used for hole filling)
- Create (`w`, `c`) * (1 bit + 15 bits) (called `w_h_s_cache`)
    - Used to store metadata regarding the interpolated frame
    - As there are 2 interpolated frames, 2 of this cache are needed
    - First bit - low if hole, high if filled
    - Following 15 bits - SAD score
    - Set all values to 0
- Stream frame into DRAM following procedure outlined for first frame
- Also stream greyscale values from frame into `target_win_cache` in parallel
- Also pull out greyscale values from the source frame into `source_win_cache`
- When `w` rows have been read in to `target_win_cache` and `source_win_cache`:
    - Continue streaming greyscale pixels into other `b` rows of `target_win_cache` from target frame
    - Taking a block from the `source_win_cache`:
        - Search the corresponding search window in `target_win_cache`
            - Returns the best motion vector and SAD score
        - Pull the other 2 channels for the block out of DRAM
        - Write the block to `write_cache` by following the motion vector
            - If the `w_h_s_cache` says the says there is a hole, write to the pixel
            - If there is no hole, only write if the SAD is lower for block being written
        - Update `w_h_s_cache` for every pixel written with the SAD score and setting the hole bit to 1
    - Do the same as the previous step in parallel but swap `source_win_cache` and `target_win_cache`
    - Repeat the last 2 stages for the whole row of blocks in both `source_win_cache` and `target_win_cache`
    - Ignoring the top 5 rows in `write_cache`, apply the median filter to any pixel that is a hole in the following `b` rows
    - Write the same `b` rows to DRAM (for the interpolated frame) and set all values to 0
    - Set the corresponding values in `w_h_s_cache` to 0
    - Shift the the start address of both the `write_cache` and `w_h_s_cache` by `b` rows
    - Repeat until whole image is read in

## Hardware Estimation:

### DRAM Writing Bandwidth:

- For each incoming frame (1/24 s):
    - Entire frame is written to DRAM:
        - 3 * `r` * `c` bytes
    - 2 interpolated frames are written to DRAM:
        - 6 * `r` * `c` bytes
    - Total:
        - 9 * `r` * `c` bytes
- Total:
    - 216 * `r` * `c` bytes / s

### DRAM Reading Bandwidth:

- For each incoming frame (1/24 s):
    - Entire previous frame is pulled out block by block (wasted data minimised)
        - 3 * `r` * `c` bytes
    - 2 channels read from the incoming frame
        - 2 * `r` * `c` bytes
- Every 1/60 s:
    - Stream out the frame for this time stamp:
        - 3 * `r` * `c` bytes
- Total:
    - 300 * `r` * `c` bytes / s

### Required Cache Size:

- To store frame block wise:
    - 6 * `b`* `c` bytes
- `source_win_cache`:
    - (`w` + `b`) * `c` bytes
- `target_win_cache`:
    - (`w` + `b`) * `c` bytes
- `write_cache` * 2:
    - 6 * (`w` + 5) * `c` bytes
- `w_h_s_cache` * 2:
    - 4 * `w` * `c`
- Total:
    - 2 * `c` * (4 * `b` + 3 * (2 * `w` + 5)) bytes

### Example Estimations:

For:
- `b` = 8
- `r` = 1080
- `c` = 1920
- `w` = 22

Results:
- DRAM write bandwidth = 427.1 MB/s
- DRAM read bandwidth = 593.3 MB/s
- Required cache size = 0.66 MB
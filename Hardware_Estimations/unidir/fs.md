# Full Search ME and Unidirectional MCI:

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

## Unidirectional Interpolation:

- Create interpolated frame
- Create `r`*`c` int32 SAD table
- Create `r`*`c` bool hole table
- For each block in the source frame:
    - Find new coordinates of block in interpolated frame (by following vector)
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

The following stage is designed to store the incoming frame in a block wise format, as apposed to raster order.

- Create (2 * `b`, `c`) * 3 bytes cache
- As the first frame streams in, place the pixels into the cache
- When `b` rows have been streamed in, start writing the cache to DRAM in a block wise fashion
    - Blocks are flattened and then written in contiguously
    - Left to right
    - Stream frame into the other `b` rows while writing
    - Repeat until full image in DRAM and stored block wise

After first frame, the following stages happen in a loop with each incoming frame:

- Create (2 * `w`, `c`) * 1 byte cache (called `win_cache`)
    - This cache will be used to search the target frame for the motion vectors
    - The height is 2*`w` so that the first `w` can be processed while the second is streamed in
- Create (`w` + `b`, `c`) * 3 bytes cache (called `write_cache`)
    - This cache is to store the interpolated frame as it's being written to save bandwidth
    - As 2 frames are interpolated between each input frame, 2 of these caches are required
    - Set top `b` rows to 0
    - Start addressing after top `b` rows (top `b` rows are only used for hole filling)
- Create (`w`, `c`) * (1 bit + 15 bits) (called `w_h_s_cache`)
    - Used to store metadata regarding the interpolated frame
    - As there are 2 interpolated frames, 2 of this cache are needed
    - First bit - low if hole, high if filled
    - Following 15 bits - SAD score
    - Set all values to 0
- Create (`b`, n * 64) * 1 byte cache (called `block_cache`)
    - Used to store the source block from the previous frame  
    - Width = n * 64, because the read from DRAM is 64 contiguous bytes (512 bits), so if `b`^2 < 512, then n=1, but if it is larger, then a larger n is required to store all of the data
- Stream frame into DRAM following procedure outlined for first frame
- Also stream greyscale values from frame into `win_cache` in parallel
- When `w` rows have been read in to `win_cache`:
    - Continue streaming greyscale pixels into other `w` rows
    - Begin pulling out the blocks from the previous frame from DRAM (that correspond to the row of windows that have just been stored in cache) and convert to greyscale
        - Cache block in `block_cache`
    - Perform full search (detailed above) for given block in `block_cache` and search window from `win_cache`
        - Output should be single motion vector with corresponding SAD score
    - Calculate new position of block in `write_cache` (relative to block row) by following motion vector
        - As there are multiple interpolated frames, this is done for both (also true for all following steps)
    - For each pixel in the block, if the corresponding location in `w_h_s_cache` says there is a hole, fill pixel in `write_cache` with pixel from block
    - For each pixel in the block, if the corresponding location in `w_h_s_cache` says there is no hole, compare SAD in `w_h_s_cache` with found SAD and keep the lowest
    - Fill `w_h_s_cache` with a 1 for the hole and then appropriate SAD score
    - After each block in the row in the source frame has been processed:
        - Ignoring the top `b` rows of `write_cache`, search the following `b` rows for pixels that have a hole value of 0 in `w_h_s_cache` in the corresponding location
        - Apply median filter to any such pixel in `write_cache`
        - Ignoring the top `b` rows of `write_cache`, write the following `b` rows into DRAM (either in block wise format for consistency when streaming out, or in raster order)
        - Shift the addressing of the `write_cache` so that the start is `b` rows later
        - Set the first `b` rows to 0 in `w_h_s_cache` (the values corresponding to the `b` rows of `write_cache` that have just been written to DRAM) and then shift the addressing so that the start is `b` rows later
    - Repeat for the next `w` rows in `win_cache`
- Repeat until entire frame has been processed

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
- Every 1/60 s:
    - Stream out the frame for this time stamp:
        - 3 * `r` * `c` bytes
- Total:
    - 252 * `r` * `c` bytes / s

### Required Cache Size:

- To store frame block wise:
    - 6 * `b`* `c` bytes
- `win_cache`:
    - 2 * `w` * `c` bytes
- `write_cache` * 2:
    - 6 * (`w` + `b`) * `c` bytes
- `w_h_s_cache` * 2:
    - 4 * `w` * `c`
- `block_cache`:
    - `b` * n * 64 bytes
    - Where n is a large enough positive integer such that: `b`^2 <= n * 512
- Total:
    - (12 * `b` * `c`) + (64 * `b` * `n`) + (12 * `c` * `w`) bytes

### Example Estimations:

For:
- `b` = 8
- `r` = 1080
- `c` = 1920
- `w` = 22

n = 1, as 8^2 < 512

- DRAM write bandwidth = 447.9 MB/s
- DRAM read bandwidth = 522.5 MB/s
- Required cache size = 691.7 KB
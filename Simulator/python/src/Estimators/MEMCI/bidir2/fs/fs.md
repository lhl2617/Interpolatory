# Full Search ME and Advanced Bidirectional MCI:

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

## Advanced Bidirectional Interpolation:

Some of the details of this algorithm are quite complex so for a detailed explanation please refer to the paper:  
"Motion-Compensated Frame Rate Up-Conversion—Part II: New Algorithms for Frame Interpolation", 2010  
by: Demin Wang, Senior Member, IEEE, André Vincent, Philip Blanchﬁeld, and Robert Klepko
https://ieeexplore.ieee.org/document/5440975   
**Note:** As the motion vectors are generated with a non-fixed technique, occlusions are not noted at the ME stage. Disregard any steps that rely on this data in the above paper.

- Calculate forward and backward motion vectors using previous algorithm
    - Swap frames to get backward motion vectors
- Create `r` * `c` interpolated frame (to store pixel values)
- Create `r` * `c` SAD table (to store SADs (errors))
- Create `r` * `c` hole table (to tell if pixel is a hole)
- Create `r` * `c` weightings table (to record number of contributions to each pixel)
- Create a second version of the above tables for the image created using the reverse motion vectors
- For the forward motion vectors:
    - Perform IEWMC to generate interpolated frame
        - Expand the source block in question and apply weightings
        - Follow the vector to the location of the block in the interpolated frame
        - Accumulate values into the appropriate entries in the 4 tables listed above
- Repeat for the backward motion vectors
- Combine forward and backward images using error-adaptive combination
- Apply BDHI to fill holes
    - As this step can operate on cached data, we will not go into further details here, as it does not contribute to the bandwidth estimation or cache scheme used

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
- Create (`w` + 2, `c`) * 3 bytes cache (called `write_cache`)
    - This cache is to store the interpolated frame as it's being written to save bandwidth
    - For each interpolated frame, create 2 caches
        - 1 for forward motion image
        - 1 for backward motion image
    - As 2 frames are interpolated between each input frame, 4 of these caches are required
    - Set top 2 rows to 0
    - Start addressing after top 2 rows (top 2 rows are only used for hole filling)
- Create (`w`, `c`) * (1 bit + 15 bits + 16 bits) (called `w_h_s_cache`)
    - Used to store metadata regarding the interpolated frame
    - For each interpolated frame, create 2 caches
        - 1 for forward motion image
        - 1 for backward motion image
    - As there are 2 interpolated frames, 4 of this cache are needed
    - First bit - low if hole, high if filled
    - Following 15 bits - Accumulated weightings
    - Following 16 bits - SAD score (error)
    - Set all values to 0
- Stream frame into DRAM following procedure outlined for first frame
- Also stream greyscale values from frame into `target_win_cache` in parallel
- Also pull out greyscale values from the source frame into `source_win_cache`
- When `w` rows have been read in to `target_win_cache` and `source_win_cache`:
    - For the forward motion image:
        - Continue streaming greyscale pixels into other `b` rows of `target_win_cache` from target frame
        - Taking a block from the `source_win_cache`:
            - Search the corresponding search window in `target_win_cache`
                - Returns the best motion vector and SAD score
            - Pull the other 2 channels for the block out of DRAM
            - Expand the block by doubling its size and apply the weighting filter
            - Write the expanded block to `write_cache` by following the motion vector
                - Change the `w_h_s_cache` for every modified pixel:
                    - to indicate that the pixel is not a hole
                    - Accumulate the SAD of the pixel
                    - Accumulate the weighting of the pixel
        - Do the same as the previous step in parallel but swap `source_win_cache` and `target_win_cache`
        - Repeat the last 2 stages for the whole row of blocks in both `source_win_cache` and `target_win_cache`
    - Repeat for the backwards motion image
    - Ignoring the top 2 rows in `write_cache`, for the following `b` rows:
        - Normalise each pixel according to its accumulated weighting
        - For each corresponding pixel in the forward and backwards cache, apply error-adaptive combination algorithm
        - Apply BDHI to fill holes (can use the 2 top in calculations)
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
- `write_cache` * 4:
    - 12 * (`w` + 2) * `c` bytes
- `w_h_s_cache` * 4:
    - 16 * `w` * `c`
- Total:
    - 2 * `c` * (4 * `b` + 15 * `w` + 12) bytes

### Example Estimations:

For:
- `b` = 8
- `r` = 1080
- `c` = 1920
- `w` = 22

Results:
- DRAM write bandwidth = 427.1 MB/s
- DRAM read bandwidth = 593.3 MB/s
- Required cache size = 1.21 MB
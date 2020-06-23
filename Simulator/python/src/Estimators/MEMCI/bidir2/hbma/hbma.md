# HBMA ME and Advanced Bidirectional MCI:

## Parameters:

- `b_max` = max size of single axis of block in pixels
- `b_min` = min size of single axis of block in pixels
- `r` = number of rows of pixels in frame
- `c` = number of columns of pixels in frame
- `w` = size of single axis of search window in pixels
- `s` = number of times the frames are downscaled

## HBMA:

- Block size must be power of 2
- Reduce first and second images `steps` times using linear filter, storing each image
    - Weightings for linear filter:
      |      |     |      |
      |------|-----|------| 
      |0.0625|0.125|0.0625| 
      |0.125 |0.25 |0.125 |
      |0.0625|0.125|0.0625|
    - Convolve filter with images with stride of (2,2) to downscale
- Perform full search algorithm on smallest first and second frames
- For next smallest images -> original images:
    - Increase motion vector density
        - Because the image size is halved when downscaled, with a consistent block size, a ("parent") block in the downscaled image is 4 ("child") blocks in the original image
        - For each of the 4 child blocks for every block in the previous iteration:
            - Search areas in a (3x3) window around position pointed to by parent vector, and the 2 vectors associated with 2 blocks adjacent to the parent block (parent vectors need to be multiplied by 2 to account for change in image size)
            - Select vector corresponding to the smallest SAD
- For `b_max` -> `b_min` by halving:
    - Increase motion vector density
        - By halving the block size, each previous ("parent") block holds 4 ("child") blocks
        - For each of the 4 child blocks for every block in the previous iteration:
            - Search areas in a (3x3) window around position pointed to by parent vector, and the 2 vectors associated with 2 blocks adjacent to the parent block
            - Select vector corresponding to the smallest SAD
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

Some required formulas:

- `a(i)` = 2^(`s` - `i`) * `w` + Sum (`n` = 1 -> `s` - `i`) (2^`n`)
- `pad` =  Sum (`n` = 1 -> log_2 (`b_max`/`b_min`)) (2^`n`)

For simplicity of explanation, `s`=1 has been used in the algorithm:

The following stage is designed to store the incoming frame in a block wise format, as apposed to raster order.

- Create (2 * `b_min`, `c`) * 3 bytes cache
    - For original frame so it can be written block wise
- Create (2 * `b_max`, `c`/2) * 1 byte cache
    - For downscaled frame so that it can be written block wise
- As the first frame streams in, place the pixels into the first cache
- When `b_max` rows have been streamed in, start writing the cache to DRAM in a block wise fashion
    - Blocks are flattened and then written in contiguously
    - Left to right
    - Channels stored separately
    - Stream frame into the other `b_max` rows while writing
    - Repeat until full image in DRAM and stored block wise
- Concurrently, when 3 rows have been streamed in, begin applying downscale filter to image and store in second cache
    - Once `b_max` rows of downscaled image have been created, save to DRAM in block wise format (as above)

After first frame, the following stages happen in a loop with each incoming frame (`target_frame`):

- Stream `target_frame` into DRAM following procedure outlined for first frame
- Create (`a(0)+pad`, `c`) * 1 byte cache (called `source_win_cache_0`)
    - This cache will be used to search the largest scale source frame for the motion vectors
    - Number of rows is `a(0)+pad`, as `a(0)` is the range of motion a block can take, and the `pad` is so that the cache can be reused for future density increases
    - 1 byte is needed because it is only the Y channel
- Create (`a(1)`, `c`/2) * 1 byte (called `source_win_cache_1`)
    - This cache will be used to search the downscaled source frame for the motion vectors
    - 1 byte needed as it is only the Y channel
- Create (`a(0)+pad`, `c`) * 1 byte cache (called `target_win_cache_0`)
    - This cache will be used to search the largest scale target frame for the motion vectors
    - Number of rows is `a(0)+pad`, as `a(0)` is the range of motion a block can take, and the `pad` is so that the cache can be reused for future density increases
    - 1 byte is needed because it is only the Y channel
- Create (`a(1)`, `c`/2) * 1 byte (called `target_win_cache_1`)
    - This cache will be used to search the downscaled target frame for the motion vectors
    - 1 byte needed as it is only the Y channel
- Create (`a(0)+pad+2`, `c`) * 3 bytes cache (called `write_cache`)
    - This cache is to store the interpolated frame as it's being written to save bandwidth
    - For each interpolated frame, create 2 caches
        - 1 for forward motion image
        - 1 for backward motion image
    - As 2 frames are interpolated between each input frame, 4 of these caches are required.
    - Set top 5 rows to 0
    - Start addressing after top 5 rows (top 5 rows are only used for hole filling)
- Create (`a(0)+pad`, `c`) * (1 bit + 15 bits + 16 bits) (called `w_h_s_cache`)
    - Used to store metadata regarding the interpolated frame
    - For each interpolated frame, create 2 caches
        - 1 for forward motion image
        - 1 for backward motion image
    - As there are 2 interpolated frames, 4 of this cache are needed
    - First bit - low if hole, high if filled
    - Following 15 bits - Accumulated weightings
    - Following 16 bits - Accumulated SAD (error)
    - Set all values to 0
- Create (2, `c`/`b_max`) * 2 bytes cache (called `forward_vec_cache_0`)
    - Used when increasing vector density for forward vectors
    - Records previous row of motion vectors
    - 1 byte for x
    - 1 byte for y
    - Initialised to 0
- Create (2, `c`/(2*`b_max`)) * 2 bytes cache (called `forward_vec_cache_1`)
    - Similar to above but for downscaled image
- Create (2, `c`/`b_max`) * 2 bytes cache (called `backward_vec_cache_0`)
    - Used when increasing vector density backward vectors
    - Records previous row of motion vectors
    - 1 byte for x
    - 1 byte for y
    - Initialised to 0
- Create (2, `c`/(2*`b_max`)) * 2 bytes cache (called `backward_vec_cache_1`)
    - Similar to above but for downscaled image
- Read into `source_win_cache_1` from the downscaled source frame in DRAM
- Read into `target_win_cache_1` from the downscaled target frame in DRAM
- Read into `source_win_cache_0` from the downscaled source frame in DRAM
- Read into `target_win_cache_0` from the downscaled target frame in DRAM
- When `a(1)` rows have been read in to both top level caches (the sub steps here are performed once in the forward direction and then in the backward direction. To perform backwards, swap `source_win_cache_n` with `target_win_cache_n` and `forward_vec_cache_n` with `backward_vec_cache_n`):
    - Read blocks sequentially from `source_win_cache_0`
    - For each block:
        - Calculate motion vector by performing a full search in `target_win_cache_0`
        - Store motion vector in `forward_vec_cache_0` for reference by its children and adjacent children
        - Read 4 children blocks from `source_win_cache_1`
        - For each child block:
            - Perform search in 27 locations (as described in HBMA section)
            - Store motion vector in `forward_vec_cache_1` for reference by its children and adjacent children
            - Break block into 4 child blocks
                - If not currently using original image, then children come from the layer above
                - If on the original image, halve the block size to get child blocks
                - For each child:
                    - Perform 27 searches as stated before
                    - If working on the original image with the min block size, follow motion vector and write child block into `write_cache` and update `w_h_s_cache` with corresponding metadata
                    - When A full row of blocks have been processed, move to the next step
- Repeat for backwards motion (writing into appropriate caches) (this can be done in parallel with previous step)
- Ignoring the top 2 rows in `write_cache`, for the following `b_min` rows:
    - Normalise each pixel according to its accumulated weighting
    - For each corresponding pixel in the forward and backwards cache, apply error-adaptive combination algorithm
    - Apply BDHI to fill holes (can use the 2 top rows in calculations)
    - Write the same `b_min` rows to DRAM (for the interpolated frame) and set all values to 0
    - Set the corresponding values in `w_h_s_cache` to 0
- Shift the the start address of both the `write_cache` and `w_h_s_cache` by `b_min` rows
- Repeat the last 4 steps until all of the image has been processed

## Hardware Estimation:

### DRAM Writing Bandwidth:

- For each incoming frame (1/24 s):
    - Frame written to DRAM:
        - 3 * `r` * `c` bytes
    - Downscaled frames written to DRAM:
        - Sum (`i` = 1 -> `s`) (`r` * `c` / 2^`i`)
    - 2 interpolated frames written to DRAM:
        - 6 * `r` * `c` bytes
    - Total:
        - 9 * `r` * `c` + Sum (`i` = 1 -> `s`) (`r` * `c` / 2^`i`) bytes
- Total:
    - (9 * `r` * `c` + Sum (`i` = 1 -> `s`) (`r` * `c` / 2^`i`)) * 24 bytes / s

### DRAM Reading Bandwidth:

- For each incoming frame (1/24 s):
    - Every image saved in DRAM is read out (only Y channel):
        - 2 * Sum (`i` = 0 -> `s`) (`r` * `c` / 2^`i`) bytes
    - 2 colour channels from original source frame:
        - 2 * `r` * `c` bytes
    - Total:
        - 2 * `r` * `c` + 2 * Sum (`i` = 0 -> `s`) (`r` * `c` / 2^`i`) bytes
- Every 1/60 s:
    - Stream out a frame:
        - 3 * `r` * `c` bytes
- Total:
    228 * `r` * `c` + 48 * Sum (`i` = 0 -> `s`) (`r` * `c` / 2^`i`) bytes / s

### Required Cache Size:

- To store frames:
    - 6 * `b_min` * `c` bytes
- To downscale and store:
    - Sum (`i` = 1 -> `s`) (2 * `b_max` * `c`/2^`i`) bytes
- `win_cache` * 2:
    - 2 * (Sum (`i` = 0 -> `s`) (`a(i)` * `c`/2^`i`) + `pad` * `c`) bytes
- `write_cache` * 4:
    - 12 * (`a(0)+pad+2`) * `c` bytes
- `w_h_s_cache` * 4:
    - 16 * (`a(0)+pad`) * `c` bytes
- `vec_cache` * 2:
    - 2 * Sum (`i` = 0 -> `s`) (4 * `c`/(2^`i` * `b_max`))

### Example estimation:

For:
- `b_max` = 8
- `b_min` = 4
- `r` = 1080
- `c` = 1920
- `w` = 22
- `s` = 2

Results:
- DRAM write bandwidth = 462.7 MB/s
- DRAM read bandwidth = 617.0 MB/s
- Required cache size = 5.49 MB
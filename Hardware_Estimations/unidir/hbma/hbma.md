# HBMA ME and Unidirectional MCI:

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
- Create (`a(0)+pad`, `c`) * 1 byte cache (called `win_cache_0`)
    - This cache will be used to search the largest scale target frame for the motion vectors
    - Number of rows is `a(0)+pad`, as `a(0)` is the range of motion a block can take, and the `pad` is so that the cache can be reused for future density increases
    - 1 byte is needed because it is only the Y channel
- Create (`a(1)`, `c`/2) * 1 byte (called `win_cache_1`)
    - This cache will be used to search the downscaled target frame for the motion vectors
    - 1 byte needed as it is only the Y channel
- Create (`a(0)+pad+5`, `c`) * 3 bytes cache (called `write_cache`)
    - This cache is to store the interpolated frame as it's being written to save bandwidth
    - As 2 frames are interpolated between each input frame, 2 of these caches are required.
    - Set top 5 rows to 0
    - Start addressing after top 5 rows (top 5 rows are only used for hole filling)
- Create (`a(0)+pad`, `c`) * (1 bit + 15 bits) (called `w_h_s_cache`)
    - Used to store metadata regarding the interpolated frame
    - As there are 2 interpolated frames, 2 of this cache are needed
    - First bit - low if hole, high if filled
    - Following 15 bits - SAD score
    - Set all values to 0
- Create (2, `c`/`b_max`) * 2 bytes cache (called `vec_cache_0`)
    - Used when increasing vector density
    - Records previous row of motion vectors
    - 1 byte for x
    - 1 byte for y
    - Initialised to 0
- Create (2, `c`/(2*`b_max`)) * 2 bytes cache (called `vec_cache_1`)
    - Similar to above but for downscaled image
- Read into `win_cache_0` from the downscaled target frame in DRAM
- When `a(1)` rows have been read in:
    - Read blocks sequentially from downscaled source frame
    - For each block:
        - Calculate motion vector by performing a full search in `win_cache_0`
        - Store motion vector in `vec_cache_0` for reference by its children and adjacent children
        - Begin reading into `win_cache_1` from level above target frame (in this case, the original image) (Y channel)
        - When `a(0)+pad` rows have been read in:
            - Read 4 children blocks from layer above source frame (in this case, the original image)
            - For each child block:
                - Perform search in 27 locations (as described in HBMA section)
                - Store motion vector in `vec_cache_1` for reference by its children and adjacent children
                - Break block into 4 child blocks
                    - If not currently using original image, then children come from the layer above
                    - If on the original image, halve the block size to get child blocks
                    - For each child:
                        - Perform 27 searches as stated before
                        - As its the original image, follow motion vector and write child block into `write_cache` and update `w_h_s_cache` with corresponding metadata
                        - When `write_cache` is full, apply hole filling filter to top `b_min` rows below the top 5 rows (they are only to provide hole filling info) and then write those rows to DRAM and shift the starting address by `b_min` rows. set corresponding rows in `w_h_s_cache` to 0 and shift the start address by the same amount

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
- `win_cache`:
    - Sum (`i` = 0 -> `s`) (`a(i)` * `c`/2^`i`) + `pad` * `c` bytes
- `write_cache` * 2:
    - 6 * (`a(0)+pad+5`) * `c` bytes
- `w_h_s_cache` * 2:
    - 4 * (`a(0)+pad`) * `c` bytes
- `vec_cache`:
    - Sum (`i` = 0 -> `s`) (4 * `c`/(2^`i` * `b_max`))

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
- Required cache size = 2.12 MB
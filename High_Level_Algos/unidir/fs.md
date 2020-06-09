# Algorithm:

## Full Search:

- For each block in first image (`source block`):
    - Calculate SAD of `source block` with blocks of matching size in a window in the second image
        - For each block in the window in the second image (`target block`):
            - Calculate SAD of `source block` and `target block` and note corresponding vector
    - Take the vector corresponding to the lowest SAD and record in output with SAD (for occlusion in MCI) (in cases where there are multiple lowest SADs, precedence should be given to the smallest vector)
- Return block-wise motion vector field

## Unidirectional Interpolation:



# Params:

- `b` = size of single axis of block
- `r` = number of rows in frame
- `c` = number of columns in frame
- `w` = size of single axis of search window

# Cache Scheme:

The first frame is read in and stored in DRAM in a block wise layout (blocks are flattened and contiguous). This requires a 2 * `b` * `c` cache, as the blocks cannot be stored until they are streamed in fully, and a second row of cache is needed so that more of the frame can be streamed in while the previous blocks are written to DRAM.


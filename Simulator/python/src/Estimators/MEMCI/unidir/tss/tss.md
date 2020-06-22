# Three Step Search ME and Unidirectional MCI:

## Parameters:

- `b` = size of single axis of block in pixels
- `r` = number of rows of pixels in frame
- `c` = number of columns of pixels in frame
- `w` = size of single axis of search window in pixels

## Three Step Search:

- For each block in first image (`source block`):
    - `center` = `source block`
    - For `step` in (`steps`-1 -> 1) (default value of `steps` is 3):
        - `space` = 2^`step`
        - For each block in 3x3 around `center`, `space` pixels apart (`target block`):
            - Calculate SAD between `source block` and `target block` and note corresponding vector (no need for `center` block as it has been previously calculated)
        - `center` = `target block` with lowest SAD
    - `space` = 1
    - For each block in 3x3 around `center`, `space` pixels apart (`target block`):
        - Calculate SAD between `source block` and `target block` and note corresponding vector (no need for `center` block as it has been previously calculated)
    - Assign vector with lowest corresponding SAD to `source block`
- Return block-wise motion vector field

## Unidirectional Interpolation:

- Create interpolated frame
- Create `r`*`c` SAD table
- Create `r`*`c` hole table
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

<!-- TODO: integrated system -->

## Hardware Estimation:

### DRAM Writing Bandwidth:

<!-- TODO: writing bandwidth -->

### DRAM Reading Bandwidth:

<!-- TODO: reading bandwidth -->

### Required Cache Size:

<!-- TODO: required cache size -->

### Example Estimations:

<!-- TODO: example estimation -->
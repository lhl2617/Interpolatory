# High Level Description of Full Search

## Algorithm:

- For each block in first image (`source block`):
    - Calculate SAD of `source block` with blocks of matching size in a window in the second image
        - For each block in the window in the second image (`target block`):
            - Calculate SAD of `source block` and `target block` and note corresponding vector
    - Take the vector corresponding to the lowest SAD and record in output with SAD (for occlusion in MCI) (in cases where there are multiple lowest SADs, precedence should be given to the smallest vector)
- Return block-wise motion vector field

## Resource Usage for No Caching:

### Parameters:

- Frame resolution: `h` x `w`
- Block size: `b`
- Window: `win`

### Pixel Accesses:

- Number of blocks in image = `h` * `w` / (`b`^2)  
- Number of comparisons needed per block = (2 * `win` + 1)^2
- Number of pixels per comparison = 2 * `b`^2
- Number of pixels accessed = 2 * `h` * `w` * (2 * `win` + 1)^2

## Cache Optimisations and Resource Usage:

### Caching source block only:

The block from the first frame is placed into cache and reused for every comparison for that block - the first frame should no longer have repeated pixel accesses.

**Cache size = `b`^2 * 3 bytes**

- Number of blocks in image = `h` * `w` / (`b`^2)  
- Number of comparisons needed per block = (2 * `win` + 1)^2
- Number of pixels per comparison = `b`^2
- Number of pixels accesses in source frame (cached so only once) = `h` * `w`
- Number of pixels accessed = `h` * `w` * (2 * `win` + 1)^2 + (`h` * `w`)

### Caching source block and target window:

The block from the previous frame is cached (as in previous) and now also the target window in the second frame. Pull the target window into cache before doing comparisons for source block.

**Cache size = (`b`^2 * 3 bytes) + ((2 * `win` + `b`)^2 * 3 bytes)**

- Number of blocks in image = `h` * `w` / (`b`^2)
- Number of pixels per block = `b`^2
- Number of pixels per target window = (2 * `win` + `b`)^2
- Number of pixels per block search = `b`^2 + (2 * `win` + `b`)^2
- Number of pixels accessed = (`h` * `w` / (`b`^2)) * (`b`^2 + (2 * `win` + `b`)^2)

### Caching source block and rolling target window:

By only removing the first column (or row) and then reading the next column (or row) when the source block moves, a lot of the target window in cache can be reused.

**Cache size = (`b`^2 * 3 bytes) + ((2 * `win` + `b`)^2 * 3 bytes)**

- Number of blocks in image = `h` * `w` / (`b`^2)
- Number of pixels per block = `b`^2
- Number of pixels for first column target window = (2 * `win` + `b`)^2
- Number of pixels per column = `b` * (2 * `win` + `b`)
- Number of blocks per row = `w` / `b`
- Number of blocks per column = `h` / `b`
- Number of pixels accessed per row = ((2 * `win` + `b`) * `h` * `w` / `b`) + (`h` * `w`)
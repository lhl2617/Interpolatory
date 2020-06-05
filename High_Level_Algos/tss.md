# High Level Description of Three Step Search

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

## Resource Usage:

### Parameters:

- Frame resolution: `h` x `w`
- Block size: `b`
- Steps: `s`

### Calculations:

- Number of blocks in image = `h` * `w` / (`b`^2)  
- Number of comparisons needed per block = 9 + (`s` - 1) * 8
- Number of pixels per comparison = 2 * `b`^2
- Number of pixels accessed = 2 * `h` * `w` * (9 + (`s` - 1) * 8)

## Cache Optimisations and Resource Usage:

### Caching source block only:

Cache size = `b`^2 * 24 bits

- Number of blocks in image = `h` * `w` / (`b`^2)  
- Number of comparisons needed per block = 9 + (`s` - 1) * 8
- Number of pixels per comparison = `b`^2
- Number of pixels accesses in source frame (cached so only once) = `h` * `w`
- Number of pixels accessed = `h` * `w` * (9 + (`s` - 1) * 8) + (`h` * `w`)

### Caching source block and target window:

Cache size = (`b`^2 * 24 bits) + (`WIN` * 24 bits)

- Number of blocks in image = `h` * `w` / (`b`^2)
- Number of pixels per block = `b`^2
- `WIN` = Number of pixels per target window = Sum (i=0 -> `s`-1) ((2^i + `b`)^2)
- Number of pixels accesses in source frame (cached so only once) = `h` * `w`
- Number of pixels accessed = (`h` * `w`) + (`h` * `w` / (`b`^2)) * Sum (i=0 -> `s`-1) ((2^i + `b`)^2)

Has a trade off - if the number of steps is too big for the block size, this becomes less efficient
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

### Writes:

- Number of motion vectors outputted = `h` * `w` / (`b`^2)
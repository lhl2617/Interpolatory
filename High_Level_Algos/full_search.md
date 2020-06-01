# High Level Description of Full Search

## Algorithm:

- For each block in first image (`source block`):
    - Calculate SAD of `source block` with blocks of matching size in a window in the second image
        - For each block in the window in the second image (`target block`):
            - Calculate SAD of `source block` and `target block` and note corresponding vector
    - Take the vector corresponding to the lowest SAD and record in output with SAD (for occlusion in MCI) (in cases where there are multiple lowest SADs, precedence should be given to the smallest vector)
- Return block-wise motion vector field

## Resource Usage:

### Parameters:

- Frame resolution: `h` x `w`
- Block size: `b`
- Window: `win`

### Pixel Accesses:

- Number of blocks in image = `h` * `w` / (`b`^2)  
- Number of comparisons needed per block = (2 * `win` + 1)^2
- Number of pixels per comparison = 2 * `b`^2
- Number of pixels accessed = 2 * `h` * `w` * (2 * `win` + 1)^2

### Writes:

- Number of motion vectors outputted = `h` * `w` / (`b`^2)
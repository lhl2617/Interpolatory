# High Level Description of Hierarchical Block Matching Algorithm

- Block size must be power of 2
- Reduce first and second images `steps` times using linear filter, storing each image
    - Weightings for linear filter:
      |      |     |      |
      |------|-----|------| 
      |0.0625|0.125|0.0625| 
      |0.125 |0.25 |0.125 |
      |0.0625|0.125|0.0625|
    - Convolve filter with images with stride of (2,2) to downscale
- Perform full search algorithm on smallest first and second images
- For next smallest images -> original images:
    - Increase motion vector density
        - Because the image size is halved when downscaled, with a consistent `block size`, a ("parent") block in the downscaled image is 4 ("child") blocks in the original image
        - For each of the 4 child blocks for every block in the previous iteration:
            - Search areas in a (2*`sub_region`+1)x(2*`sub_region`+1) window (default value for `sub_region` is 1) around position pointed to by parent vector, and the 2 vectors associated with 2 blocks adjacent to the parent block (parent vectors need to be multiplied by 2 to account for change in image size)
            - Select vector corresponding to the smallest SAD
- For `block size` -> `min block size` by halving:
    - Increase motion vector density
        - By halving the `block size`, each previous ("parent") block holds 4 ("child") blocks
        - For each of the 4 child blocks for every block in the previous iteration:
            - Search areas in a (2*`sub_region`+1)x(2*`sub_region`+1) window (default value for `sub_region` is 1) around position pointed to by parent vector, and the 2 vectors associated with 2 blocks adjacent to the parent block
            - Select vector corresponding to the smallest SAD
- Return block-wise motion vector field

## Resource Usage:

### Parameters:

- Frame resolution: `h` x `w`
- Block size: `b`
- Steps: `s`
- Window size: `win`
- Sub window size: `s_win`
- Min block size: `m_b`

### Pixel Accesses:

#### Downscaling:

Calculating number of pixel access to downscale each frame `s` times

- Number of pixels in `i`th downscaled image = `h` * `w` / 4^`i`
- Number of pixels in filter application = 9
- Number of pixels accessed to downscale `i`th image = `h` * `w` * 9 / 4^`i`
- `DS_TOT` = Overall pixel accesses for downscaling `s` times = Sum (`i` = 1 -> `s`) (`h` * `w` * 9 / 4^`i`)

#### Full Search:

- Number of blocks in smallest image = `h` * `w` / (`b`^2 * 4^`s`)  
- Number of comparisons needed per block = (2 * `win` + 1)^2
- Number of pixels per comparison = 2 * `b`^2
- `FS_TOT` = Number of pixel accesses = 2 * `h` * `w` * (2 * `win` + 1)^2  / 4^`s`

#### Upscaling Vector Density Increase:

- `BLOCKS`<sub>`i`</sub> = Number of blocks in `i`th image = `h` * `w` / (`b`^2 * 4^`i`)
- `COMPS` = Number of comparisons per block = 3 * (2 * `s_win` + 1)^2
- `PIXS` = Number of pixels per comparison = 2 * `b`^2 
- `VECS` = Number of vector accesses per block = 3
- `UVDI_TOT` = Number of data accesses = Sum (i = 0 -> `s`-1) ((`COMPS` * `PIXS` + `VECS`) * `BLOCKS`<sub>`i`</sub>)

#### Block Size Downscaling Vector Density Increase:

- `BLOCKS`<sub>`i`</sub> = Number of blocks in image with block size `i` = `h` * `w` / (`i`^2)
- `COMPS` = Number of comparisons per block = 3 * (2 * `s_win` + 1)^2
- `PIXS`<sub>`i`</sub> = Number of pixels per comparison with block size `i` = 2 * `i`^2 
- `VECS` = Number of vector accesses per block = 3
- `BSDVI_TOT` = Number of data accesses = Sum (i = `b` / 2 -> `m_b` : `i` / 2) ((`COMPS` * `PIXS`<sub>`i`</sub> + `VECS`) * `BLOCKS`<sub>`i`</sub>)

#### Total Accesses:

- Total data accesses = `DS_TOT` + `FS_TOT` + `UVDI_TOT` + `BSDVI_TOT`
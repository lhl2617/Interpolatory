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
- For next smallest images -> original images (`first/second curr_img`):
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
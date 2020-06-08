# Interpolator Documentation
## Nearest
- Name: `Nearest`
- Description: Known as drop/repeat. Nearest frame in point of time is used

## Oversample
- Name: `Oversample`
- Description: Similar to nearest except frames at boundaries are blended (oversampled)

## Linear
- Name: `Linear`
- Description: Bilinear interpolation in which new frames are created by blending frames by their weights w.r.t. time

## Blur
- Name: `Blur`
- Description: Downconverts frame rate and blends frames, supports only downconversion by 2 to the n where n is an integer

## Speed
- Name: `Speed`
- Description: Converts frame rate by simply changing the speed of the video. No frame is created nor dropped.

## MEMCI
- Name: `MEMCI`
- Description: Motion Estimation & Motion Compensated Interpolation method.
### Options
- `me_mode`
    - Which Motion Estimation method to use.
    - Default: `hbma`
    - Possible values: 
        * `hbma`: Hierarchical Block Matching Algorithm
        * `fs`: Full Search
        * `tss`: Three Step Search
- `block_size`
    - Block size (positive integer) used by ME
    - Default: `8`
- `target_region`
    - The distance in pixels (positive integer) that the algorithm searches for motion
    - Default: `3`
- `mci_mode`
    - Which Motion Compensated Interpolation method to use.
    - Default: `unidir`
    - Possible values: 
        * `unidir`: Unidirectional Method
        * `bidir`: Bidirectional Method
        * `unidir2`: Improved Bidirectional Method
- `filter_mode`
    - Which filtering method to use.
    - Default: `weighted_mean`
    - Possible values: 
        * `mean`: Mean
        * `median`: Median
        * `weighted`: Weighted Mean
- `filter_size`
    - Filter size (positive integer) used by MCI filter method
    - Default: `5`

## SepConv-CUDA
- Name: `SepConv-CUDA`
- Description: SepConv kernel-based method. Requires CUDA dependencies. Supports only upconversion by a factor of 2 or if the factor has denominator 2 (e.g. 2.5 = 5/2). For the latter case, upconversion is done at a doubled factor and a pair of frames are blended to create one output frame.
### Options
- `model`
    - Specify which model to use
    - Default: `l1`
    - Possible values: 
        * `l1`: Using the L1 model (benchmark optimised)
        * `lf`: Using the Lf model (qualitative results optimised)

## RRIN-CUDA
- Name: `RRIN-CUDA`
- Description: Residue Refinement method. Requires CUDA dependencies.
### Options
- `flow_usage_method`
    - How the flow between two images is used.
    - Default: `linear`
    - Possible values: 
        * `midframe`: Uses only midpoint of flow to interpolate output flow. Supports only upconversion by a factor of 2 or if the factor has denominator 2 (e.g. 2.5 = 5/2). For the latter case, upconversion is done at a doubled factor and a pair of frames are blended to create one output frame.
        * `linear`: Uses bilinear interpolation based on the flow between two consecutive original frames.

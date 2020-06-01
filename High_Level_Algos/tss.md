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
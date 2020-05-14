# Intel Video Interpolation Goals

This project is split into 3 phases, with Phase 3 being a stretch goal.

## Phase 1 - Literature review to investigate existing algorithms 
* Study existing literature for video frame-rate up conversion (FRUC)
* Collect, summarise and review relevant papers, from papers reviewing trivial algorithms to state-of-the-art methods

### Success metrics
* Succinct summary and comparison of existing algorithms, from trivial to state-of-the-art
    * To give the reader an overview of past research and methods used in both industry and research
* Focus on feasibility of algorithms on hardware, but also future-proof with advanced algorithms
    * As review is intended for a future FPGA IP team, emphasis is put on hardware-feasible algorithms, but discussion also extends to advanced algorithms should hardware capabilities improve in the future
* Short background on different methods proposed, including their advantages and disadvantages
    * To give a short overview of different methods to enable comparison among them
* A reliable resource for a future team with minimal knowledge of FRUC to get up-to-speed with existing algorithms and research
    * To enable our clients to understand quickly FRUC concepts

## Phase 2 - Software implementation of a small number of algorithms of interest
* Implement testbench and framework for video interpolation
* Implement trivial algorithms (nearest-neighbour, bilinear interpolation, oversampling)
* Choose algorithm that balances both feasibility (on hardware) and quality to implement in software (Python). This means that advanced methods using CNNs are disqualified, as well as trivial algorithms (albeit implemented as a reference). After discussion, MEMC algorithms with varying components are chosen for the balance between feasibility and quality.
* Benchmark algorithms based on existing datasets
* Stretch: Investigation of basic CNN algorithms and research into feasibility on hardware

### Success metrics
* Framework able to perform FRUC, minimally 24-to-60fps, with stretch goal being 25-to-60fps and 50-to-60fps
    * Produce output videos that can be visually inspected for qualitative quality comparisons
* Testbench and framework able to produce PSNR and SSIM scores for the widely-used interpolation test dataset: Middlebury 
    * To produce a quantitative metric for quality
* Testbench and framework able to record runtime and memory resources required for each algorithm
    * To compare runtime of different algorithms
    * To give an indication of how memory-intensive an algorithm is
* Trivial algorithms implemented
    * For referencing purposes, and to compare quantitative quality and runtime metrics
* MEMC algorithms implemented
    * Main goal of Phase 2, working MEMC algorithms to study improvement in quality of interpolated frames as well as compare runtime and qualitative qualities
* Stretch: A number of CNN algorithms implemented
    * To allow analysis and comparison of state-of-the-art methods, and to gain a deeper understanding into CNN algorithm feasibility on hardware
* Key metrics for algorithm analysis:
    1. Runtime: Ratio of time taken to length of input video
    2. Resource usage: Profiled/Calculated memory usage
    3. Quantitative Quality: PSNR, SSIM on Middlebury dataset
    4. Qualitative Quality: Visual inspection of output video to ensure no judder/artifacts


#### Notes
Benchmarking Device: Python 3 on `corona50.doc.ic.ac.uk`, (Intel Core-i7 8700; 16GB RAM)

## Phase 3 - (Stretch) Proposal of high level hardware architecture
* Choose most suitable algorithm based on software simulations and experiments in Phase 2
* Propose hardware architecture required for estimation of block RAM usage and DDR bandwidth required

### Success metrics 
* To be discussed after Phase 2

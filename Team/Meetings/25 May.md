# 25 May

## Progress so far

- LH
    - Implemented 3 ML algorithms (2.5/3)
    - Made the GUI
    - Made the prelim. leaflet 

- Olly/Naim 
    - ME - FS, TSS, HBMA
        - HBMA isolate motion fields best (refer dog dance), faster
        - runtime: HBMA fastest
    - Smoothing (median, mean, weighted mean)
        
- Navid
    - MCI - ran some benchmarks but still too slow to be tractable
    - filling
    - HBMA TODO
    - unidirectional

- Bruce
    - bidirectional (worse than unidirectional, don't know why)
        - 2x runtime
        
- Charles
    - Ran tests for unidirectional with combinations, block size, params. etc.
        - PSNR/SSIM/Runtime
        - found 5 best combinations
            - 4 weighted mean
            - <13 seconds
        - HBMA to be investigated


### TODO

- LH
    - Kieron, George progress report ideally two weeks
    - Merge
        - Merge my ML branch into master
            - Save a copy of their current branch   
                - git merge master
    
    - Leaflet, Naim hardware (today)
    - GUI finish up
    - Finish up 3rd ML

- Olly/Naim
    - implement some of the algos in C++
    - HBMA further (MAP, statistical approach used in hardware) 
    investigate
    
- Navid
    - investigate further on the MCI methods (today)
    - Middlebury limiting
        - UCF101, Vimeo90K testbench
        PSNR/SSIM

- Bruce
    - Continue on bidirectional investigation 
        - explanation 
    - Write end-to-end testbench for MEMCI
        - PR into master
    
- Charles 
    - fine tune HBMA

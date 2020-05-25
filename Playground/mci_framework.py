
# I will make a very rough skeleton

def MCI(frame1, frame2, flow, ratio):
    #using pseudo code:
    #unidirectional
    
    num_of_interpolation = floor(ratio)+1 
    #applying smoothmotion, conveting from 24 to 60 FPS, ratio is 2.5, interpolating 2 more frames. 
    #the reason for adding 1 is the temporal position of two frames are at t+1/3 and t+2/3

    InteporlatedFrame #initialising a empty frame with each pixel has [,,,] 'r,g,b,SAD'

    for i in range(1, num_of_interpolation):
        for each pixel in frame1:
        #coordinates represented by (u,v)
            u,v = pixel.coordinates + flow.(x,y)*i / num_of_interpolation
            if InteporlatedFrame(u,v) == [-1,-1,-1,10000] or flow.sad < InteporlatedFrame(u,v).sad
            #change the pixel when the position is empty or the new pixel has smaller SAD.
                InteporlatedFrame(u,v) = pixel

    formating(InteporlatedFrame) #get rid of SAD value in each pixel

    # fill the holes by median filter: 
    # need to try different kernel size, I will use 3x3 here
    ksize = 3
    median_f = generate_kernel(ksize)# I am not sure this is possible because median filter is not constant, maybe use other way to do the filtering
    InteporlatedFrame = scipy.signal.convolve2d(InteporlatedFrame, median_f ,mode='same', boundary='fill',fillvalue=0)

    return InteporlatedFrame

def MCI_Video(video, ratio):
    for i in range (0, frames-1)
        MV = ME(video[i],video[i+1])
        outputvideo += MCI(video[i],video[i+1], MV, ratio)
    postprocessing(outputvideo) #when doing 2.5 converting, the avaraging (A+B)/2 should be done here









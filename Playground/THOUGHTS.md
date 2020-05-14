# Stuff

#### Temporal frame interpolation.
Given a low frame rate
video, a temporal frame interpolation algorithm generates
a high frame rate video by synthesizing additional frames
between two temporally neighboring frames. Specifically,
let I1 and I3 be two consecutive frames in an input video, the
task is to estimate the missing middle frame I2. Temporal
frame interpolation doubles the video frame rate, and can be
recursively applied to generate even higher frame rates.

## Existing programs

### SmoothVideo Project (SVP)
- Tried this myself, works fairly well
- Not open source, not even free for Mac/Windows but free for Linux
- Also not `free` software
- Works on 720p YouTube content fairly well
- Should work well on fairly new machines for 1080p content
- Supports live interpolation for local footage/streaming
- Has customisable quality/modes
- Actually uses ffmpeg in the backend, not sure how
- Uses fast motion interpolation, no implementation details available

### ffmpeg
- [https://github.com/FFmpeg/FFmpeg/tree/21dd05ee6ad3fccfd57a7171a8d8d882d9abf940](https://github.com/FFmpeg/FFmpeg/tree/21dd05ee6ad3fccfd57a7171a8d8d882d9abf940)
- open source & free GNU Lesser General Public License version 2.1
- has couple of modes
- mostly C
- forum mentioned motion interpolation is very slow compared to SVP

### mvp
- [https://mpv.io/](https://mpv.io/)
- [https://github.com/mpv-player/mpv](https://github.com/mpv-player/mpv)
- GNU General Public License GPL version 2
- Mostly C
- open source & free
- very naive implementation, more so than ffmpeg
- [Interpolation wiki](https://github.com/mpv-player/mpv/wiki/Interpolation)
- Has `sphinx` (said to be slow by haasn)

### Butterflow
- Python
- [https://github.com/dthpham/butterflow](https://github.com/dthpham/butterflow)
- MIT license
- Not sure about speed etc., no paper (uses [Farneback algorithm](http://www.diva-portal.org/smash/get/diva2:273847/FULLTEXT01.pdf))
- Looks `ok` on sample clips on YouTube

### DAINAPP (Depth-Aware Video Frame Interpolation)
- From the Wenbo Bao paper - https://grisk.itch.io/dain-app
- This application only work in NVIDIA cards, since it require CUDA to work. Even execution on CUDA it take a long time to render, most likely would take months rendering in the CPU, so a CPU version might never come out. (SLOW!)

### MVTools
- To investigate
- (Used by `haasn` as an example motion in https://github.com/haasn/interpolation-samples)

## Existing Frameworks
### OpenCV
https://docs.opencv.org/3.4/d4/dee/tutorial_optical_flow.html

## Papers and stuff

NB: Occured to me that usage of these evaluation techniques would be rather impossible, but still, useful to gauge from leaderboards what kind of algos are doing great, some has comprehensive lists of algos.

Also a caveat is that for leaderboards of optical flow you won't see results for other algos using different methods, for example Niklaus' method (2 in algos below) that uses convolutional kernels to generate a frame.
 
The flow algorithms result in a computation of a "flow vector", http://vision.middlebury.edu/flow/submit/ has code on how to do it.
### Evaluation (Optical Flow)
#### Summary

| Item | Dataset | Requires Submission for scoring | Leaderboard |
| ---- | ------- | ------------------- | ----------- |
| 1 | O | O | O |
| 2 | O | O | X |
| 3 | O | O | X |
| 4 | O | O | O |

#### Details

1. A Database and Evaluation Methodology for Optical Flow (2007, 2011)
    - Link: http://vision.middlebury.edu/flow/floweval-ijcv2011.pdf
    - Details:
        - "The classic optical flow evaluation benchmark", most optical flow papers submit their algos for this evaluation
        - Not freely available however, requires submisison via http://vision.middlebury.edu/flow/submit/
        - needs paper submission
        - we can however use the dataset provided on the site http://vision.middlebury.edu/flow/data
        - has existing results and leaderboard so we can see what's good

    - Usage here - produces score! https://github.com/sniklaus/sepconv-slomo/blob/master/benchmark.py

2. Robust Vision Challenge (2020, still ongoing)
    - Link: https://github.com/ozendelait/rvc_devkit/tree/release/flow
    - Details: 
        - A contest, still ongoing
        - Can use the dataset but will not have numerical results
        - no live leaderboard yet, still ongoing

3. MPI Sintel Flow Dataset
    - Link: http://sintel.is.tue.mpg.de/
    - Details:
        - A data set for the evaluation of optical flow derived from the open source 3D animated short film, Sintel.
        - Same as the other two, need to submit to get results
        - Dataset available

4. KITTI Vision Benchmark Suite - Optical Flow Evaluation 2015
    - Link: http://www.cvlibs.net/datasets/kitti/eval_scene_flow.php?benchmark=flow
    - Details:
        - Focused on vehicular
        - Needs to submit
        - Dataset available
        - Has leaderboard

### Some more useful datasets/videos
1. Big Buck Bunny (Open movie project)
    - haasn's [repo](https://github.com/haasn/interpolation-samples/blob/master/README.md) and stuff has pre-prepared clips in different framerates

2. https://standaloneinstaller.com/blog/big-list-of-sample-videos-for-testers-124.html
    - no framerate specific stuff

3. http://trace.eas.asu.edu/yuv/
    - YUV sequences, no framerate specific stuff

4. UCF101
    - UCF101 is an action recognition data set of realistic action videos, collected from YouTube, having 101 action categories. This data set is an extension of UCF50 data set which has 50 action categories.
    - https://www.crcv.ucf.edu/data/UCF101.php

5. Vimeo-90K
    - http://toflow.csail.mit.edu/index.html#original_video
    - This dataset consists of 89,800 video clips downloaded from vimeo.com, which covers large variaty of scenes and actions. It is designed for the following four video processing tasks: temporal frame interpolation, video denoising, video deblocking, and video super-resolution.

6. Adobe 240-fps dataset
    - http://www.cs.ubc.ca/labs/imager/tr/2017/DeepVideoDeblurring/

### Actual algorithms

It has occurred to me after compilation that most of the papers I found and reviewed are mostly not suitable to real-time systems for current hardware--these are very modern takes on interpolation. 

However, they give us a glimpse on many different possible methods used for interpolation, and the advantage of being advanced models is that they review simpler, older models.

A lot of the models seen run on CUDA, so Colab might be needed, but I don't think those are FPGA hardware feasible.

1. Depth-Aware Video Frame Interpolation (DAIN)
    - https://www.youtube.com/watch?v=B1Dk_9k6l08
    - https://sites.google.com/view/wenbobao/dain
    - Abstract
        - Video frame interpolation aims to synthesize nonexistent frames in-between the original frames. While significant advances have been made from the recent deep
convolutional neural networks, the quality of interpolation is often reduced due to large object motion or occlusion. In this work, we propose a video frame interpolation method which explicitly detects the occlusion by exploring the depth information. Specifically, we develop a
depth-aware flow projection layer to synthesize intermediate flows that preferably sample closer objects than farther ones. In addition, we learn hierarchical features to
gather contextual information from neighboring pixels. The
proposed model then warps the input frames, depth maps,
and contextual features based on the optical flow and local interpolation kernels for synthesizing the output frame.
Our model is compact, efficient, and fully differentiable.
Quantitative and qualitative results demonstrate that the
proposed model performs favorably against state-of-the-art
frame interpolation methods on a wide variety of datasets.
The source code and pre-trained model are available at
https://github.com/baowenbo/DAIN
    - Colab available, https://colab.research.google.com/drive/1gzsfDV_MIdehr7Y8ZzWjTuW-mMZRP4Vy
    - App available (DAIN-app), can only run on NViDIA CUDA
    - Training seems to take forever, but model works really well and looks like SOTA based on results
    - Possible to load model?
    - Pros: 
        - Results look really good 
    - Cons:
        - Implementing a runner for this model on FPGA would be painful--they are only limiting the model to CUDA machines now, don't think it's feasible for FPGA/OpenCL implementation
        - Very VRAM hungry, probably not possible for real-time, but interesting evaluation metrics and standard
        - In 4.4 (Discussions and limitations), seems very trivial drawbacks.
        - Relies on optical flow, depth info, etc., very resource-heavy


2. Video Frame Interpolation via Adaptive Separable Convolution
    - https://www.youtube.com/watch?v=T_g6S3f0Z5I
    - http://content.sniklaus.com/sepconv/video.mp4
    - https://github.com/sniklaus/sepconv-slomo
    - https://arxiv.org/pdf/1708.01692.pdf
    - Abstract
        - Standard video frame interpolation methods first estimate optical flow between input frames and then synthesize an intermediate frame guided by motion. Recent approaches merge these two steps into a single convolution
process by convolving input frames with spatially adaptive
kernels that account for motion and re-sampling simultaneously. These methods require large kernels to handle large
motion, which limits the number of pixels whose kernels can
be estimated at once due to the large memory demand. To
address this problem, this paper formulates frame interpolation as local separable convolution over input frames using pairs of 1D kernels. Compared to regular 2D kernels,
the 1D kernels require significantly fewer parameters to be
estimated. Our method develops a deep fully convolutional
neural network that takes two input frames and estimates
pairs of 1D kernels for all pixels simultaneously. Since our
method is able to estimate kernels and synthesizes the whole
video frame at once, it allows for the incorporation of perceptual loss to train the neural network to produce visually pleasing frames. This deep neural network is trained
end-to-end using widely available video data without any
human annotation. Both qualitative and quantitative experiments show that our method provides a practical solution
to high-quality video frame interpolation.
    - Pros
        - Results look really good too
        - Does not rely on optical flow (computationally-expensive)
        - Produces convolution kernels
    - Cons
        - Again, not sure how difficult for convolution kernels to be done in hardware

3. Blurry Video Frame Interpolation
    - Not directly related but explanation on deblurring required, implemented by Sony: https://www.youtube.com/watch?v=mssESTnWtUo
    - https://arxiv.org/abs/2002.12259
    - https://github.com/laomao0/BIN
    - Abstract
        - Existing works reduce motion blur and up-convert frame
rate through two separate ways, including frame deblurring and frame interpolation. However, few studies have
approached the joint video enhancement problem, namely
synthesizing high-frame-rate clear results from low-framerate blurry inputs. In this paper, we propose a blurry video
frame interpolation method to reduce motion blur and upconvert frame rate simultaneously. Specifically, we develop
a pyramid module to cyclically synthesize clear intermediate frames. The pyramid module features adjustable spatial receptive field and temporal scope, thus contributing
to controllable computational complexity and restoration
ability. Besides, we propose an inter-pyramid recurrent
module to connect sequential models to exploit the temporal relationship. The pyramid module integrates a recurrent module, thus can iteratively synthesize temporally
smooth results without significantly increasing the model
size. Extensive experimental results demonstrate that our
method performs favorably against state-of-the-art methods. The source code and pre-trained model are available
at https://github.com/laomao0/BIN.
    - Pros:
        - These seems to be what's used by Sony BRAVIA TVs, proven in industry
        - An alternative to the widely popular optical flow, if optical flow is not feasible then this is a good method
        - Has good links to old methods that only deblurring _then_ interpolation
    - Cons:
        - Also pre-trained model

4. Frame Rate Up-Conversion Based on Motion-Region Segmentation
    - https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=7805437
    - Abstract
        - The key problem of frame rate up-conversion
(FRUC) is to obtain true motion vectors (MV), especially for
the motion boundaries. In this paper, we propose a novel FRUC
algorithm based on motion-region segmentation. According to
region’s temporal consistency, motion-regions are determined by
a categorization of detected feature points’ true MVs. Then,
constrained by MV’s spatial smoothness within a region, true
motions are propagated to the entire frame. This motion-region
segmentation based method achieves truthful motion vector
field and preferable interpolated frames. Experiments show that
comparing to the state-of-art methods, the proposed algorithm
produces videos with better quality in terms of objective and
subjective evaluation.
    - Pros:
        - Seem to look doable and briefly resembles what Kieron talked about in first meeting (about motion tracking)
        - Only inspiration - very novel.
    - Cons: 
        - Experimental, no implementation so far. Model looks very _novel_, don't think it's useful as an implementation guide, but contains useful info.

5. Softmax Splatting for Video Frame Interpolation
    - https://arxiv.org/pdf/2003.05534.pdf
    - https://github.com/sniklaus/softmax-splatting
    - Abstract
        - Differentiable image sampling in the form of backward
warping has seen broad adoption in tasks like depth estimation and optical flow prediction. In contrast, how to perform forward warping has seen less attention, partly due to
additional challenges such as resolving the conflict of mapping multiple pixels to the same target location in a differentiable way. We propose softmax splatting to address
this paradigm shift and show its effectiveness on the application of frame interpolation. Specifically, given two input
frames, we forward-warp the frames and their feature pyramid representations based on an optical flow estimate using
softmax splatting. In doing so, the softmax splatting seamlessly handles cases where multiple source pixels map to
the same target location. We then use a synthesis network
to predict the interpolation result from the warped representations. Our softmax splatting allows us to not only interpolate frames at an arbitrary time but also to fine tune the
feature pyramid and the optical flow. We show that our synthesis approach, empowered by softmax splatting, achieves
new state-of-the-art results for video frame interpolation.
    - Pros:
        - Quote: `new state-of-the-art`
    - Cons:
        - Complex, resource heavy, slow

6. Super SloMo: High Quality Estimation of Multiple Intermediate Frames for Video Interpolation
    - https://www.youtube.com/watch?v=LBezOcnNJ68
    - Abstract
        - Given two consecutive frames, video interpolation aims at generating intermediate frame(s) to form both spatially and temporally coherent video sequences. While most existing methods focus on single-frame interpolation, we propose an end-to-end convolutional neural network for variable-length multi-frame video interpolation, where the motion interpretation and occlusion reasoning are jointly modeled. We start by computing bi-directional optical flow between the input images using a U-Net architecture. These flows are then linearly combined at each time step to approximate the intermediate bi-directional optical flows. These approximate flows, however, only work well in locally smooth regions and produce artifacts around motion boundaries. To address this shortcoming, we employ another U-Net to refine the approximated flow and also predict soft visibility maps. Finally, the two input images are warped and linearly fused to form each intermediate frame. By applying the visibility maps to the warped images before fusion, we exclude the contribution of occluded pixels to the interpolated intermediate frame to avoid artifacts. Since none of our learned network parameters are time-dependent, our approach is able to produce as many intermediate frames as needed. We use 1,132 video clips with 240-fps, containing 300K individual video frames, to train our network. Experimental results on several datasets, predicting different numbers of interpolated frames, demonstrate that our approach performs consistently better than existing methods.
    - Pros
        - NVIDIA endorsed, going to be implemented in NVIDIA NGX Technology - AI for Visual Applications
        - Results don't look as good as 1/2.
    - Cons
        - Very proprietary and complex
        - Not meant to be real time
        - No code/models (A: Unfortunately, we are unable to publish the code. Implementation of SuperSloMo in PyTorch is pretty straightforward. Feel free to contact Huaizu Jiang in case of any questions.)
        - Slow, not possible, but interesting (it takes 0.97s and 0.79s to generate 7 intermediate frames given two images of 1280*720 resolution on single NVIDIA GTX 1080Ti and Tesla V100 GPUs, respectively.)


https://ieeexplore.ieee.org/document/8334253

https://ieeexplore.ieee.org/document/7805437

https://arxiv.org/abs/1810.08768

https://ieeexplore.ieee.org/document/6323027

https://ieeexplore.ieee.org/abstract/document/6958822

https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=9023270
Deep Learning Approach to Video Frame Rate
Up-Conversion Using Bilateral Motion Estimation

https://www.researchgate.net/publication/333941419_Spatio-Temporal_Convolutional_Neural_Network_for_Frame_Rate_Up-Conversion
Spatio-Temporal Convolutional Neural Network for Frame Rate Up-Conversion

https://www.researchgate.net/publication/340043690_A_Stacked_Deep_MEMC_Network_for_Frame_Rate_up_Conversion_and_Its_Application_to_HEVC
Download citation	Share 	Download full-text PDF
A Stacked Deep MEMC Network for Frame Rate up Conversion and Its Application to HEVC

https://www.youtube.com/watch?v=W3HLBexyb0U
Video Frame Interpolation via Adaptive Convolution | Spotlight 2-1B

youtube.com/watch?v=8HtA6iyJkHo
Frame Rate Upscaling with Neural Networks



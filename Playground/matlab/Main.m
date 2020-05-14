% target frame rate
targetRate = 60;
disp("targetRate: " + targetRate);

% maximum number of frames to output, set as Inf for all frames
maxOutFrames = Inf;
disp("maxOutFrames: " + maxOutFrames);

% input video paths
inputPathRoot = "../interpolation-samples/converted/";
videoPaths = ["30fps/native.m4v", "20fps/native.m4v"];

% interpolation modes 
interpolationModes = [InterpolationMode.Nearest, InterpolationMode.Oversample];



for videoPath = videoPaths
    fullVideoPath = inputPathRoot + videoPath;
    videoIn = VideoReader(fullVideoPath);
    
    for interpolationMode = interpolationModes 
        disp("Processing " + videoPath + " with mode " + char(interpolationMode));
        
        outFilename = getOutputVideoPath(videoPath, interpolationMode, maxOutFrames);
        
        tic
        InterpolateVideo(videoIn, targetRate, maxOutFrames, interpolationMode, outFilename);
        toc
    end
end


function [outputVideoPath] = getOutputVideoPath(inputVideoPath, interpolationMode, maxOutFrames)
    maxOutSuffix = "";
    if (maxOutFrames ~= Inf)
        maxOutSuffix = "_"  + maxOutFrames;
    end
    outputVideoPath = "output/" + extractBetween(inputVideoPath, 1, 5) + "/" + char(interpolationMode) + maxOutSuffix;
end
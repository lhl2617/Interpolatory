function [] = InterpolateVideo(videoIn, targetRate, maxOutFrames, interpolationMode, outFileName)
% videoIn: input VideoReader object
% maxOutFrames: maximum number of frames to output, set as Inf for all frames
% interpolationMode: Interpolation Mode

    videoIn.CurrentTime = 0;
    sourceRate = videoIn.FrameRate;
%     disp("sourceRate is " + sourceRate);
%     disp("targetRate is " + targetRate);
    if (sourceRate >= targetRate)
        error("sourceRate cannot be larger or equals to targetRate");
    end
    
%     TODO:- output raw AVI
    videoOut = VideoWriter(outFileName, "MPEG-4");
    videoOut.FrameRate = targetRate;
    videoOut.Quality = 75; % default

    open(videoOut)
    i = 1;
    totalOutputFramesPossible = floor(videoIn.Duration * targetRate);
    
    if (maxOutFrames > totalOutputFramesPossible)
        maxOutFrames = totalOutputFramesPossible;
    end
    

    % if we don't need real time this can be parallelised
    for i = 1:maxOutFrames
        if (mod(i, targetRate) == 0) 
            disp("Frame " + i + "/" + maxOutFrames + " | " + (i * 100 ./ maxOutFrames) + "%");
        end
        frame = GetInterpolatedFrame(videoIn, targetRate, interpolationMode, i);
        writeVideo(videoOut, frame);
    end

    close(videoOut)
end


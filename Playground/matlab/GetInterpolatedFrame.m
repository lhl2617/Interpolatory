function [outFrame] = GetInterpolatedFrame(videoIn, targetRate, interpolationMode, targetFrameNum)
% videoIn: VideoReader
% targetRate: target frame rate 
% interpolationMode: one of the enums in InterpolationMode.m
% targetFrameNum: frame number required (1-indexed)
    sourceRate = videoIn.FrameRate;
    
    if (sourceRate >= targetRate)
        error("sourceRate cannot be larger or equals to targetRate");
    end
    
    switch interpolationMode
        case InterpolationMode.Nearest
            outFrame = nearest(videoIn, targetFrameNum, sourceRate, targetRate);
        case InterpolationMode.Oversample
            outFrame = oversample(videoIn, targetFrameNum, sourceRate, targetRate);
        case InterpolationMode.Linear
            outFrame = linear(videoIn, targetFrameNum, sourceRate, targetRate);
        otherwise 
            error("interpolationMode \"" + interpolationMode + "\" not implemented.");
    end
end

%
%   e.g. 24->60
%   A A A B B C C C D D
%
%   e.g. 25->30
%   A A B C D E F 
%
function [outFrame] = nearest(videoIn, targetFrameNum, sourceRate, targetRate)
    rateRatio = targetRate ./ sourceRate;
    sourceFrameNum = floor((targetFrameNum - 1) ./ rateRatio);
    
    % WARNING: 1-indexed
    frameNum = sourceFrameNum + 1;
%     disp("targetFrame: " + targetFrameNum + ", using sourceFrame: " +
%     frameNum);
    outFrame = read(videoIn, frameNum);
end

%
%   e.g. 24->60 (rateRatio 2.5, period 5)
%   A A (A+B)/2 B B (B+C)/2 C C (C+D)/2 E E
%
%   e.g. 25->30 (rateRatio 1.2, period 6)
%   A .2A+.8B .4B+.6C .6C+.4D .8D+.2E E F
%
function [outFrame] = oversample(videoIn, targetFrameNum, sourceRate, targetRate)
    % blend the crossovers
    % display each frame rateRatio times
    rateRatio = targetRate ./ sourceRate;
    
    % this period is the number of frame in the targetRate
    % before a cycle occurs (e.g. in the 24->60 case it occurs between B &
    % C at period = 5
    [period, ~] = rat(rateRatio);
    
    % which targetFrame (0-indexed) is this after a period
    offset = floor(mod((targetFrameNum - 1), period));
    
    % a key frame is a source frame that matches in time, this key frame
    % (0-indexed) is the latest possible source frame
    keyFrameNum = floor((targetFrameNum - 1) ./ period) * period;
    
    rateRatiosFromKeyFrame = floor(offset ./ rateRatio);
    
    distanceFromNextRateRatioPoint = (rateRatiosFromKeyFrame + 1) * rateRatio - offset;
    if (distanceFromNextRateRatioPoint >= 1) 
        frameNum = floor(keyFrameNum ./ rateRatio + rateRatiosFromKeyFrame) + 1;
        % disp("targetFrame: " + targetFrameNum + ", using sourceFrame: " + frameNum);
        
        outFrame = read(videoIn, frameNum);
    else
        
        frameAn = floor(keyFrameNum ./ rateRatio + rateRatiosFromKeyFrame) + 1;
        frameBn = frameAn + 1;
        % guard
        if (frameAn >= videoIn.NumFrames)
           if (frameAn > videoIn.NumFrames)
               error("Requiring a frame that is not available, index too large");
           else 
               outFrame = read(videoIn, frameAn);
                % disp("targetFrame: " + targetFrameNum + ", using sourceFrame: " + frameAn);
           end
        else 
            frameA = read(videoIn, frameAn);
            frameB = read(videoIn, frameBn);
            weightA = distanceFromNextRateRatioPoint;
            weightB = 1 - weightA;

            outFrame = blendFrame(frameA, weightA, frameB, weightB);

            % disp("targetFrame: " + targetFrameNum + ", using sourceFrame: " + weightA + "*" + frameAn + " + " + weightB + "*" + frameBn);
        end
    end
    
end

%
%   e.g. 24->60 (rateRatio 2.5, period 5)
%   A (1.5A+B)/2.5 (0.5A+2B)/2.5 (2B+0.5C)/2.5 (B+1.5C)/2.5 
%
%
function [outFrame] = linear(videoIn, targetFrameNum, sourceRate, targetRate)
    rateRatio = targetRate ./ sourceRate;
    
    % this period is the number of frame in the targetRate
    % before a cycle occurs (e.g. in the 24->60 case it occurs between B &
    % C at period = 5
    [period, ~] = rat(rateRatio);
    
    % which targetFrame (0-indexed) is this after a period
    offset = floor(mod((targetFrameNum - 1), period));
    
    % a key frame is a source frame that matches in time, this key frame
    % (0-indexed) is the latest possible source frame
    keyFrameNum = floor((targetFrameNum - 1) ./ period) * period;
    
    rateRatiosFromKeyFrame = floor(offset ./ rateRatio);
    distanceFromPrevRateRatioPoint = offset - (rateRatiosFromKeyFrame) * rateRatio;
    
    frameAn = floor(keyFrameNum ./ rateRatio + rateRatiosFromKeyFrame) + 1;
    frameBn = frameAn + 1;
    
    % guard
    if (frameAn >= videoIn.NumFrames)
       if (frameAn > videoIn.NumFrames)
           error("Requiring a frame that is not available, index too large");
       else 
           outFrame = read(videoIn, frameAn);
                % disp("targetFrame: " + targetFrameNum + ", using sourceFrame: " + frameAn);
       end
    else 
        frameA = read(videoIn, frameAn);
        frameB = read(videoIn, frameBn);

        weightA = (rateRatio - distanceFromPrevRateRatioPoint) ./ rateRatio;
        weightB = 1 - weightA;

        % disp("targetFrame: " + targetFrameNum + ", using sourceFrame: " + weightA + "*" + frameAn + " + " + weightB + "*" + frameBn);
        outFrame = blendFrame(frameA, weightA, frameB, weightB);
    end
end

function [outFrame] = blendFrame(frameA, weightA, frameB, weightB)

% - errors 

%     if (weightA < 0 || weightB < 0 || weightA > 1 || weightB > 1)
%         error('weights must be positive and between 0 and 1 inclusive')
%     end
% 
%     if (~isalmost(weightA + weightB, 1, 0.01))
%         error('Blend frame weights must add up to 1');
%     end
%     
%     if (size(frameA) ~= size(frameB))
%        error('Dimensions of blended frames do not match'); 
%     end
   
    
    
    outFrame = round(weightA * frameA + weightB * frameB);
     
    
end

% https://uk.mathworks.com/matlabcentral/fileexchange/15816-isalmost
function test = isalmost(a,b,tol)
%
% usage: test = isalmost(a,b,tol)
%
% tests if matrix a is approximately equal to b within a specified 
% tolerance interval (b-tol <= a <= b+tol)
%
% note:  if b is given as a scalar, all values in a are compared against
%        the scalar value b
%
% calls: none
%
% inputs:
%
% a(nr,nc) = matrix of data values to test
% b(nr,nc) = matrix of data values for comparison (or a single scalar value)
%      tol = tolerance used in computation
%
% outputs:
%
% test(nr,nc) = matrix of test results:
%
%        test(i,j) = 0 -> a(i,j) is not equal to b(i,j) (or is NaN)
%        test(i,j) = 1 -> a(i,j) is approximately equal to b(i,j)
%
%   author : James Crawford 
%   created 01/08/2007
%
%   history: v1.0 (01/08/2007)
%
% get length of input matrix a
[nr,nc] = size(a);
% check input for consistency
if ~all(size(a) == size(b))
   if all(size(b) == [1 1])
      % convert scalar value b to a matrix of size(a)
      b = b*ones(size(a));
   else
      disp('error: input arguments are inconsistent (isalmost.m)')
      disp('(b) must be a matrix of same size as (a) or a single value')
   end
end
one = ones(size(b));
% perform test
test = (a <= b+tol*one)&(a >= b-tol*one);
%

end
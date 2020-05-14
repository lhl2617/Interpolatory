# import imageio
# import math
# from io import BytesIO
# import time

# debug = False

# file = open('../interpolation-samples/24fps/native.mkv', 'rb')
# content = file.read()
# vid = imageio.get_reader(BytesIO(content), 'ffmpeg')

# metadata = vid.get_meta_data()

# print(metadata)

# def nearest(targetFrameNum, sourceRate, targetRate):
#   rateRatio = targetRate / sourceRate
#   sourceFrameNum = math.floor(targetFrameNum / rateRatio)

#   if debug: 
#     print(f'targetFrame: {targetFrameNum}, using sourceFrame: {sourceFrameNum}')
#   # return videoIn[sourceFrameNum] 
#   return vid.get_data(sourceFrameNum)

# sourceRate = metadata["fps"]
# targetRate = 60

# videoOut = imageio.get_writer('./test.mkv', fps=targetRate)

# maxOutFrames = int(metadata["duration"] * targetRate)

# start = int(round(time.time() * 1000))
# for i in range(maxOutFrames):
#   if (i % targetRate == 0):
#     print(f'Frame {i} / {maxOutFrames} | {100 * i / maxOutFrames} %')
#   frame = nearest(i, sourceRate, targetRate)
#   videoOut.append_data(frame)

# end = int(round(time.time() * 1000))
# print(f'Took {(end-start) / 1000} seconds');
# videoOut.close()
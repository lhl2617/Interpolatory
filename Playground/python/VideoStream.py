from collections import deque

'''
A base VideoStream that stores video data.

Derived for video_stream objects. This class defines methods that _MUST_ be overriden
This is useful if we end up needing more complex VideoStreams with advanced functions
'''

class BaseVideoStream:
    def __init__(self):
        self.nframes = None
        self.fps = None
        self.size = None
        self.duration = None
        return

    def get_frame(self, idx):
        raise Exception('get_frame not implemented in VideoStream!')

'''
Stores the video, also has cache for frames to increase speed,
also helpful to keep track of currently required frames
as per resources.

video remains constant here and is not mutated
'''

class VideoStream(BaseVideoStream):
    def __init__(self, video, max_cache_size, preload=True):

        if (max_cache_size < 0):
            raise Exception('max_cache_size needs to be at least 0')

        self.video = video

        # metadata info
        self.video_metadata = video.get_meta_data()
        self.nframes = self.video_metadata['nframes']
        self.fps = self.video_metadata['fps']
        self.size = self.video_metadata['size']
        self.duration = self.video_metadata['duration']

        self.max_cache_size = max_cache_size

        # actual cache
        self.cache = deque()
        self.cache_start_idx = 0
        self.cache_end_idx = -1

        if preload:
            self.preload_cache()

    # return the frame from the cache if possible
    # this assumes that video is read sequentially
    # otherwise it would be better to use a ordered map structure
    # the implementation is a sequential window cache
    # not sure if FPGA DDR can implement this

    # further reading: traversal caches: https://www.hindawi.com/journals/ijrc/2010/652620/
    def get_frame(self, idx):
        # not using cache
        if (self.max_cache_size == 0):
            return self.video.get_data(idx)

        # whether in cache
        in_cache = (idx >= self.cache_start_idx and idx <= self.cache_end_idx)

        if (not in_cache):
            # not in cache and can't re enter from front
            # e.g. if cache holds [4, 5] and need 3
            if (idx < self.cache_start_idx):
                return self.video.get_data(idx)

            # not in cache and can't enter from back
            # e.g. if cache holds [4, 5] and need 7 (not 6)
            if (idx - self.cache_end_idx > 1):
                return self.video.get_data(idx)

            # if cache is max size evict the earliest
            if (len(self.cache) == self.max_cache_size):
                # print(f'evict {self.cache_start_idx}')
                self.cache.popleft()
                self.cache_start_idx += 1

            # print(f'add {idx}')
            # add to back of cache
            frame = self.video.get_data(idx)
            self.cache.append(frame)
            self.cache_end_idx += 1

        cache_idx = idx - self.cache_start_idx

        # print(f'Getting {idx}, cache_idx {cache_idx} ranges: {self.cache_start_idx, self.cache_end_idx}')
        return self.cache[cache_idx]

    # preload into cache
    # warning: might run out of memory
    def preload_cache(self):
        # print('preloading into ache')
        frames_to_preload = min(self.max_cache_size, self.nframes)

        for i in range(frames_to_preload):
            self.get_frame(i)
        # print('finished preloading into cache')

class BenchmarkVideoStream(BaseVideoStream):
    def __init__(self, frame_1, frame_2):
        self.frame_1 = frame_1
        self.frame_2 = frame_2
        
        self.nframes = 2
        self.fps = 1
        # self.size # this is not used
        self.duration = 2
        

    def get_frame(self, idx):
        if idx == 0:
            return self.frame_1
        elif idx == 1:
            return self.frame_2
        raise Exception(f'Tried to get invalid frame idx {idx}')


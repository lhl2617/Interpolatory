
class Bi(BaseInterpolator):
    def __init___(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size)

    def get_interpolated_frame(self, idx):

        source_frame_idx = math.floor(idx/self.rate_ratio)
        source_frame = self.video_stream.get_frame(source_frame_idx)

        dist = idx/self.rate_ratio - math.floor(idx/self.rate_ratio)

        if dist == 0:
            return source_frame


        if not self.MV_field_idx < idx/self.rate_ratio < self.MV_field_idx+1:
            target_frame = self.video_stream.get_frame(source_frame_idx+1)
            #self.MV_field = get_motion_vectors(4, 10, source_frame, target_frame)
            self.MV_field_idx = source_frame_idx

            '''
            fwd = get_motion_vectors(4, 10, source_frame, target_frame)
            bwd = get_motion_vectors(4, 10, target_frame, source_frame)

            if fwd[,,2]>bwd[,,2]: #use the one with smaller SAD
                self.MV_field = bwd
                dist = 1 - dist
            else :
                self.MV_field = fwd

            self.MV_field_idx = source_frame_idx
            '''
            fwd = get_motion_vectors(4, 10, source_frame, target_frame)
            bwd = get_motion_vectors(4, 10, target_frame, source_frame)
            self.MV_field = fwd
        Interpolated_Frame =  np.ones(source_frame.shape, dtype='float64')*-1
        SAD_interpolated_frame = np.full([source_frame.shape[0],source_frame.shape[1]],np.inf)


        for u in range(0, source_frame.shape[0]):
            for v in range(0, source_frame.shape[1]):
                if fwd[u,v,2]>bwd[u,v,2]:
                    dist = 1.0-dist
                    u_i = int(u + round(bwd[u,v,0]*dist))
                    v_i = int(v + round(bwd[u,v,1]*dist))

                    if  bwd[u,v,2] <= SAD_interpolated_frame[u_i, v_i]:

                        Interpolated_Frame[u_i, v_i] =  source_frame[u, v]
                        SAD_interpolated_frame[u_i, v_i] = bwd[u,v,2]
                        self.MV_field[u,v] = bwd[u,v]

                        #self.MV_field[u,v,0] = bwd[u,v,0]
                        #self.MV_field[u,v,1] = bwd[u,v,1]
                        #self.MV_field[u,v,2] = bwd[u,v,2]
                       
                else:
                    u_i = int(u + round(fwd[u,v,0]*dist))
                    v_i = int(v + round(fwd[u,v,1]*dist))

                    if  fwd[u,v,2] <= SAD_interpolated_frame[u_i, v_i]:

                        Interpolated_Frame[u_i, v_i] =  source_frame[u, v]
                        SAD_interpolated_frame[u_i, v_i] = fwd[u,v,2]


        k=5 #Median filter size = (2k+1)x(2k+1)
        for u in range(0, Interpolated_Frame.shape[0]):
            for v in range(0, Interpolated_Frame.shape[1]):
                if Interpolated_Frame[u,v,0] == -1:
                    u_min=max(0,u-k)
                    u_max=min(Interpolated_Frame.shape[0],u+k+1)
                    v_min=max(0,v-k)
                    v_max=min(Interpolated_Frame.shape[1],v+k+1)
                    Interpolated_Frame[u,v,0] = np.median(Interpolated_Frame[u_min:u_max,v_min:v_max,0])
                    Interpolated_Frame[u,v,1] = np.median(Interpolated_Frame[u_min:u_max,v_min:v_max,1])
                    Interpolated_Frame[u,v,2] = np.median(Interpolated_Frame[u_min:u_max,v_min:v_max,2])


        return Interpolated_Frame

    def __str__(self):
        return 'BI'
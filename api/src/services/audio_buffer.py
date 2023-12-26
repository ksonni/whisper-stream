import numpy as np

from config import Config

class AudioBuffer:
    def __init__(self, sampling_rate=Config.sampling_rate):
        self.__buffer = np.array([], dtype=np.float32)
        self.__sampling_rate = sampling_rate
        self.__current_start_time = 0

    def current_start_time(self) -> int:
        return self.__current_start_time
    
    def current_end_time(self) -> int:
        n_seconds = (self.__buffer.size/self.__sampling_rate)
        n_milis = round(n_seconds*1000)
        return self.__current_start_time + n_milis
    
    def prune_before_time(self, time_milis: int):
        if time_milis < self.current_start_time():
            return
        interval_milis = (time_milis - self.__current_start_time)
        interval_seconds = interval_milis / 1000
        n_frames: int =  round(interval_seconds / self.__sampling_rate)
        if len(self.__buffer) > n_frames:
            self.__buffer = np.delete(self.__buffer, slice(n_frames))
        else:
            self.__buffer = np.empty_like(self.__buffer)
        self.__current_start_time = time_milis 
    
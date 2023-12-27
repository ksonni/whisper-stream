import math

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
        n_seconds = (self.__buffer.size / self.__sampling_rate)
        n_milis = round(n_seconds * 1000)
        return self.__current_start_time + n_milis

    def append(self, frames: np.ndarray):
        self.__buffer = np.concatenate((self.__buffer, frames))

    def size(self) -> int:
        return self.__buffer.size

    def prune_until_time(self, time_milis: int):
        if time_milis < self.__current_start_time:
            return
        duration_sec = (time_milis - self.__current_start_time) / 1000
        n_frames = math.floor(duration_sec * self.__sampling_rate)
        n_range = slice(min(n_frames, self.__buffer.size))
        self.__buffer = np.delete(self.__buffer, n_range)
        self.__current_start_time = time_milis

    # TODO: not ideal
    def bytes(self) -> np.ndarray:
        return self.__buffer

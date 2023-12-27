import math

import numpy as np

from config import Config


class AudioBuffer:
    def __init__(self, buffer=np.array([], dtype=np.float32),
                 start_time=0, sampling_rate=Config.sampling_rate):
        self.__buffer = buffer
        self.__sampling_rate = sampling_rate
        self.__start_time = start_time

    @property
    def start_time(self) -> int:
        return self.__start_time

    @property
    def end_time(self) -> int:
        n_seconds = (self.__buffer.size / self.__sampling_rate)
        n_millis = round(n_seconds * 1000)
        return self.__start_time + n_millis

    @property
    def size(self) -> int:
        return self.__buffer.size

    def append(self, frames: np.ndarray):
        self.__buffer = np.concatenate((self.__buffer, frames))

    def prune_until_time(self, time_millis: int):
        if time_millis < self.__start_time:
            return
        duration_sec = (time_millis - self.__start_time) / 1000
        n_frames = math.floor(duration_sec * self.__sampling_rate)
        n_range = slice(min(n_frames, self.__buffer.size))
        self.__buffer = np.delete(self.__buffer, n_range)
        self.__start_time = time_millis

    def bytes(self) -> np.ndarray:
        return self.__buffer

    def copy(self) -> 'AudioBuffer':
        return AudioBuffer(self.__buffer.copy(), self.__start_time, self.__sampling_rate)

from typing import List

import numpy as np

from config import Config
from .audio_buffer import AudioBuffer
from .transcribe import TranscriptionResult


class AudioChunkManager:
    def __init__(self):
        self.__buffer = AudioBuffer()
        self.__results: List[TranscriptionResult] = []

    @property
    def has_min_buffer(self) -> bool:
        return self.__buffer.size >= Config.sampling_rate

    def copy_buffer(self) -> AudioBuffer:
        return self.__buffer.copy()

    def append_audio(self, data: np.ndarray):
        self.__buffer.append(data)

    def append_result(self, result: TranscriptionResult):
        self.__results.append(result)

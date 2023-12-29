from typing import List

import numpy as np

from config import Config
from .audio_buffer import AudioBuffer
from .transcribe import TranscriptionResult, TranscriptionChunk


class AudioChunkManager:
    def __init__(self):
        self.__buffer = AudioBuffer()
        self.__results: List[TranscriptionResult] = []

    @property
    def has_min_buffer(self) -> bool:
        return self.__buffer.size >= 2 * Config.sampling_rate

    def copy_buffer(self) -> AudioBuffer:
        return self.__buffer.copy()

    def append_audio_chunk(self, data: np.ndarray):
        self.__buffer.append(data)

    def append_transcription_result(self, result: TranscriptionResult):
        self.__results.append(result)
        if len(self.__results) > Config.min_stable_transcriptions:
            self.__results = self.__results[Config.min_stable_transcriptions - 1:]

    def prune_chunks(self):
        prune_time = self.get_prunable_time()
        if prune_time is None:
            return
        print(f'Pruning chunks before {prune_time / 1000:.2f}s')
        self.__buffer.prune_until_time(prune_time)

    def get_prunable_time(self) -> int | None:
        min_results = Config.min_stable_transcriptions
        if len(self.__results) < min_results:
            return None

        results = self.__results[:min_results]
        n_chunks = len(min(results, key=lambda r: len(r.chunks)).chunks)
        prunable_chunk: TranscriptionChunk | None = None

        for i in range(0, n_chunks):
            chunk = results[len(results)-1].chunks[i]
            if all(r.chunks[i].text == chunk.text for r in results):
                prunable_chunk = chunk
            else:
                break

        return prunable_chunk.end_time if prunable_chunk is not None else None

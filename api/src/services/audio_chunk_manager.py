import numpy as np
import protobufs.transcription_pb2 as pb

from typing import List


class AudioChunkManager:
    def __init__(self):
        self.buffer = np.array([], dtype=np.float32)
        self.results: List[pb.TranscriptionResult] = []

    def append_audio(self, data: np.ndarray):
        self.buffer = np.concatenate((self.buffer, data))

    def append_result(self, result: pb.TranscriptionResult):
        self.results.append(result)

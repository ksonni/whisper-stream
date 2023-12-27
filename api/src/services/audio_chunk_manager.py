import numpy as np
import protobufs.transcription_pb2 as pb

from typing import List
from .audio_buffer import AudioBuffer

class AudioChunkManager:
    def __init__(self):
        self.buffer = AudioBuffer()
        self.results: List[pb.TranscriptionResult] = []

    def append_audio(self, data: np.ndarray):
        self.buffer.append(data)

    def append_result(self, result: pb.TranscriptionResult):
        self.results.append(result)

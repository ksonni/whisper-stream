import numpy as np

class AudioChunkManager:
    def __init__(self):
        self.buffer = np.array([], dtype=np.float32)

    def append_audio(self, data: np.ndarray):
        self.buffer = np.concatenate((self.buffer, data))

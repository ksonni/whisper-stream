import math
import unittest

import numpy as np

from config import Config
from .audio_buffer import AudioBuffer


class TestAudioBuffer(unittest.TestCase):

    def test_init(self):
        b = AudioBuffer()
        self.assertEqual(b.start_time, 0)
        self.assertEqual(b.end_time, 0)

    def test_end_time(self):
        b = AudioBuffer()
        append_frames(b, 5)
        self.assertEqual(b.end_time, 5000)

    def test_pruning(self):
        b = AudioBuffer()
        append_frames(b, 5)
        b.prune_until_time(1000)
        self.assertEqual(b.size, 4 * Config.sampling_rate)
        self.assertEqual(b.start_time, 1000)

        b.prune_until_time(800)  # before start, so nothing happens
        self.assertEqual(b.size, 4 * Config.sampling_rate)
        self.assertEqual(b.start_time, 1000)

        b.prune_until_time(5000)
        self.assertEqual(b.size, 0)
        self.assertEqual(b.start_time, 5000)

        b.prune_until_time(6000)  # longer than current buffer
        self.assertEqual(b.size, 0)
        self.assertEqual(b.start_time, 6000)


def append_frames(b: AudioBuffer, time_sec: float):
    b.append(np.zeros(math.floor(time_sec * Config.sampling_rate), dtype=np.float32))

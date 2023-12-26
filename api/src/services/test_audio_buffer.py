import unittest

from .audio_buffer import AudioBuffer

class TestAudioBuffer(unittest.TestCase):

    def test_init(self):
        e = AudioBuffer()
        self.assertEqual(e.current_start_time(), 0)
        self.assertEqual(e.current_end_time(), 0)


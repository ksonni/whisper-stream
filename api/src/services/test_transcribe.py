import unittest
from uuid import uuid4 as uuid

import numpy as np

from .audio_buffer import AudioBuffer
from .transcribe import TranscriptionChunk, TranscriptionResult, TranscriptionParams


class TestTranscriptionResult(unittest.TestCase):

    def test_merge_chunks_start(self):
        chunks = [
            TranscriptionChunk(0, 10, 'a'),
            TranscriptionChunk(10, 12, 'b'),
            TranscriptionChunk(13, 15, 'a'),
            TranscriptionChunk(16, 23, 'a'),
        ]
        merged = TranscriptionResult.merge_chunks(chunks)
        self.assertEqual(merged, [
            TranscriptionChunk(0, 12, 'ab'),
            TranscriptionChunk(13, 15, 'a'),
            TranscriptionChunk(16, 23, 'a'),
        ])

    def test_merge_chunks_mid(self):
        chunks = [
            TranscriptionChunk(0, 10, 'a'),
            TranscriptionChunk(11, 12, 'b'),
            TranscriptionChunk(12, 15, 'c'),
            TranscriptionChunk(15, 23, 'd'),
            TranscriptionChunk(27, 31, 'e'),
        ]
        merged = TranscriptionResult.merge_chunks(chunks)
        self.assertEqual(merged, [
            TranscriptionChunk(0, 10, 'a'),
            TranscriptionChunk(11, 23, 'bcd'),
            TranscriptionChunk(27, 31, 'e'),
        ])

    def test_merge_chunks_end(self):
        chunks = [
            TranscriptionChunk(0, 10, 'a'),
            TranscriptionChunk(12, 15, 'c'),
            TranscriptionChunk(15, 31, 'e'),
        ]
        merged = TranscriptionResult.merge_chunks(chunks)
        self.assertEqual(merged, [
            TranscriptionChunk(0, 10, 'a'),
            TranscriptionChunk(12, 31, 'ce'),
        ])

    def test_init_empty(self):
        params = _make_params()
        result = TranscriptionResult(params, {})
        self.assertEqual(result.chunks, [])
        self.assertEqual(result.buffer_start, params.buffer.start_time)
        self.assertEqual(result.buffer_end, params.buffer.end_time)

    def test_init_incomplete_chunks(self):
        params = _make_params()
        result = TranscriptionResult(params, {
            'chunks': [
                {'text': 'a', 'timestamp': (0.01, 0.02)},
                {'text': 'b', 'timestamp': (0.05, None)}
            ],
        })
        self.assertEqual(result.chunks, [
            TranscriptionChunk(10, 20, 'a'),
            TranscriptionChunk(50, params.buffer.end_time, 'b'),
        ])


def _make_params() -> TranscriptionParams:
    return TranscriptionParams(
        uuid(),
        AudioBuffer(np.zeros(100, dtype=np.float32))
    )

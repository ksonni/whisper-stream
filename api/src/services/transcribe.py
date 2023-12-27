import time
from dataclasses import dataclass
from typing import Dict, List
from uuid import UUID

import torch
from transformers import pipeline, Pipeline

from config import Config
from .audio_buffer import AudioBuffer


@dataclass
class TranscriptionParams:
    id: UUID
    buffer: AudioBuffer


@dataclass
class TranscriptionChunk:
    start_time: int
    end_time: int
    text: str


class TranscriptionResult:
    def __init__(self, params: TranscriptionParams, result: Dict | None):
        self.id: UUID = params.id
        self.start: int = params.buffer.start_time
        self.end: int = params.buffer.end_time
        self.chunks: List[TranscriptionChunk] | None = None
        if result is not None:
            self.chunks = self.parse_chunks(result)

    def parse_chunks(self, result: Dict) -> List[TranscriptionChunk]:
        raw_chunks: List[Dict] = []
        if 'chunks' in result and result['chunks'] is not None:
            raw_chunks = result['chunks']
        return self.merge_chunks(list(map(self.parse_chunk, raw_chunks)))

    def parse_chunk(self, output: Dict) -> TranscriptionChunk:
        chunk = TranscriptionChunk(self.start, self.end, '')
        if 'timestamp' in output and output['timestamp'] is not None:
            timestamp: tuple[float, float] = output['timestamp']
            # Convert to millis relative to the buffer start
            if len(timestamp) > 0 and timestamp[0] is not None:
                chunk.start_time = self.start + round(timestamp[0] * 1000)
            if len(timestamp) > 1 and timestamp[1] is not None:
                chunk.end_time = self.start + round(timestamp[1] * 1000)
        if 'text' in output and output['text'] is not None:
            chunk.text = output['text']
        return chunk

    @staticmethod
    def merge_chunks(chunks: List[TranscriptionChunk]) -> List[TranscriptionChunk]:
        if len(chunks) <= 1:
            return chunks
        out: List[TranscriptionChunk] = [chunks[0]]
        current = chunks[0]
        for i in range(1, len(chunks)):
            if current.end_time == chunks[i].start_time:
                current.end_time = chunks[i].end_time
                current.text += chunks[i].text
            else:
                current = chunks[i]
                out.append(current)
        return out


def transcribe_safe(r: TranscriptionParams, sample_rate=Config.sampling_rate) -> TranscriptionResult:
    start = time.time()
    try:
        print(f'Transcribing chunk of duration {r.buffer.size / sample_rate:.2f}s')
        out = WhisperModel.transcribe(r.buffer.bytes(), chunk_length_s=24, return_timestamps=True)
        print(f'Transcribed chunk in {time.time() - start:.2f}s')
        return TranscriptionResult(r, out)
    except Exception as e:
        print(f'Transcribe chunk failed in {time.time() - start:.2f}s', e)
        return TranscriptionResult(r, None)


# Helpers

class __Model:
    def __init__(self):
        self.__pipeline: Pipeline | bool = False

    @property
    def transcribe(self) -> Pipeline:
        if isinstance(self.__pipeline, Pipeline):
            return self.__pipeline
        return self.load()

    def load(self) -> Pipeline:
        pipe = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-base.en",
            torch_dtype=torch.float16,
            device="cuda:0" if torch.cuda.is_available() else "mps",
        )
        self.__pipeline = pipe
        return pipe


WhisperModel = __Model()

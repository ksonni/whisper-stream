import time
import torch
import numpy as np
import protobufs.transcription_pb2 as pb

from transformers import pipeline
from typing import Dict, List
from config import Config
from dataclasses import dataclass

lib_transcribe = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-base.en",
    torch_dtype=torch.float16,
    device="cuda:0" if torch.cuda.is_available() else "mps",
)

# Need to use this because proto isn't picklable :(
@dataclass
class RawTranscriptionResult:
    timestamp: int
    result: Dict | None

def transcribe_safe(data: np.ndarray, timestamp: int, sample_rate=Config.sampling_rate) -> RawTranscriptionResult:
    start = time.time()
    try:
        print(f'Transcribing chunk of duration {data.size/sample_rate:.2f}s')
        out = lib_transcribe(data, chunk_length_s=24, return_timestamps=True)
        print(f'Transcribed chunk in {time.time()-start:.2f}s')
        return RawTranscriptionResult(timestamp, out)
    except Exception as e:
        print(f'Transcribe chunk failed in {time.time()-start:.2f}s', e)
        return RawTranscriptionResult(timestamp, None)

# Helpers

def decode_raw_result(r: RawTranscriptionResult) -> RawTranscriptionResult:
    raw_chunks: List[Dict] = []
    output = r.result
    if output is not None and 'chunks' in output:
        raw_chunks = output['chunks']
    return pb.TranscriptionResult(
        timestamp=r.timestamp,
        code=200 if output is not None else 500,
        chunks=map(__build_chunk, raw_chunks),
    )

def __build_chunk(output: Dict) -> pb.TranscriptionChunk:
    chunk = pb.TranscriptionChunk()
    if 'timestamp' in output:
        timestamp: tuple[float, float] = output['timestamp']
        if len(timestamp) > 0:
            chunk.start_time = round(timestamp[0] * 1000) # Convert to millis
        if len(timestamp) > 1:
            chunk.end_time = round(timestamp[1] * 1000) # Convert to millis
    if 'text' in output:
        chunk.text = output['text']
    return chunk

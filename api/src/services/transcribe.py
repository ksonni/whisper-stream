import time
import torch
import numpy as np

from transformers import pipeline
from typing import Dict
from dataclasses import dataclass

lib_transcribe = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-base.en",
    torch_dtype=torch.float16,
    device="cuda:0" if torch.cuda.is_available() else "mps",
)

@dataclass
class TranscribeResult:
    timestamp: int 
    result: Dict | None

def transcribe_safe(data: np.ndarray, timestamp: int, sample_rate=16_000) -> TranscribeResult:
    start = time.time()
    try:
        print(f'Transcribing chunk of duration {data.size/sample_rate:.2f}s')
        out = lib_transcribe(data, chunk_length_s=24, return_timestamps=True)
        print(f'Transcribed chunk in {time.time()-start:.2f}s')
        return TranscribeResult(timestamp, out)
    except Exception as e:
        print(f'Transcribe chunk failed in {time.time()-start:.2f}s', e)
        return TranscribeResult(timestamp, None)

import time
import torch

from transformers import pipeline
from transformers.pipelines.audio_utils import ffmpeg_read
import numpy as np
from uuid import UUID

from typing import Dict

from dataclasses import dataclass

lib_transcribe = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-base.en",
    torch_dtype=torch.float16,
    device="mps", # TODO: get this working with cpu if mps/cuda isn't available
)

@dataclass
class TranscribeResult:
    serial: int 
    result: Dict | None

def transcribe_safe(byte_data: bytes, serial: int, sample_rate=16_000) -> TranscribeResult:
    start = time.time()
    try:
        data: np.ndarray = ffmpeg_read(byte_data, sample_rate)
        print(f'Transcribing chunk of duration {data.size/sample_rate:.2f}s')
        out = lib_transcribe(data, chunk_length_s=24)
        print(f'Transcribed chunk in {time.time()-start:.2f}s')
        return TranscribeResult(serial, out)
    except Exception as e:
        print(f'Transcribe chunk failed in {time.time()-start:.2f}s', e)
        return TranscribeResult(serial, None)

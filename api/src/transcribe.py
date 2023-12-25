import time
import torch

from transformers import pipeline
from transformers.pipelines.audio_utils import ffmpeg_read

lib_transcribe = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-base.en",
    torch_dtype=torch.float16,
    device="mps", # TODO: get this working with cpu if mps/cuda isn't available
)

async def transcribe_safe(byte_data, sample_rate=16_000):
    start = time.time()
    try:
        data = ffmpeg_read(byte_data, sample_rate)
        out = lib_transcribe(data)
        print(f'Transcribed chunk in {time.time()-start:.2f}s')
        return out
    except Exception as e:
        print(f'Transcribe chunk failed in {time.time()-start:.2f}s', e)
        return None 

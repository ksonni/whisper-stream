import threading
import os, stat
import uuid
import time
import torch

from transformers import pipeline

def make_pipeline():
    pipe = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-base.en",
        torch_dtype=torch.float16,
        device="cuda:0" if torch.cuda.is_available() else "mps",
    )
    return pipe

lib_transcribe = make_pipeline()

async def transcribe_opus(data):
    start = time.time()
    path = f'chunk-{str(uuid.uuid1())}.opus'

    os.mkfifo(path)

    results = [None]
    supply_thread = threading.Thread(target=write_to_pipe, args=(path,data))
    processing_thread = threading.Thread(target=transcribe, args=(path,results,))

    supply_thread.start()
    processing_thread.start()
    processing_thread.join()
    supply_thread.join()

    clear_pipe(path)

    print(f'Transcribed {path} in {time.time()-start:.2f}s')

    return results[0]


def clear_pipe(path):
    if os.path.exists(path) and stat.S_ISFIFO(os.stat(path).st_mode):
        os.unlink(path)


def write_to_pipe(path, data):
    with open(path, 'wb') as f:
        f.write(data)


def transcribe(path, results):
    try:
        results[0] = lib_transcribe(path) 
    except Exception as e:
        print(f'Transcribe of pipe {path} failed', e)
        results[0] = { "error": True }

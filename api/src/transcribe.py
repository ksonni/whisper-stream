import threading
import os, stat
import whisper
import uuid
import time

from whisper.audio import load_audio

model = whisper.load_model("base.en")

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
        ar = load_audio(path)
        results[0] = model.transcribe(ar, fp16=False)
    except Exception as e:
        print(f'Transcribe of pipe {path} failed', e)
        results[0] = { "error": True }

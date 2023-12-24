import threading
import os, stat
import whisper
import uuid

model = whisper.load_model("base")

async def transcribe_opus(data):
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

    return results[0]


def clear_pipe(path):
    if os.path.exists(path) and stat.S_ISFIFO(os.stat(path).st_mode):
        os.unlink(path)


def write_to_pipe(path, data):
    with open(path, 'wb') as f:
        f.write(data)


def transcribe(path, results):
    try:
        results[0] = model.transcribe(path, fp16=False)
    except Exception as e:
        print(f'Transcribe of pipe {path} failed', e)
        results[0] = { "error": True }

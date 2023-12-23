import asyncio
import websockets
import numpy as np
import whisper

model = whisper.load_model("base")
connected = set()

async def observe_websocket(ws):
    connected.add(ws)
    print("Websocket: opened")
    try:
        async for message in ws:
            transcribe_message(message)
    except websockets.ConnectionClosed as e:
        print("Websocket: closed abnormally", e)
    finally:
        print("Websocket: closed")
        connected.remove(ws)

def transcribe_message(message):
    with open('binary.opus', 'wb') as f:
        f.write(message)
    # ar = np.frombuffer(data, dtype=np.uint8)
    # result = model.transcribe(ar.flatten().astype(np.float32) / 32768.0)
    result = model.transcribe("binary.opus", fp16=False)
    print(result['text'])

print("Starting server on port 3000")

start_server = websockets.serve(observe_websocket, "localhost", 3000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

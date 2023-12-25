import asyncio
import websockets
import json

from transcribe import transcribe_safe

connected = set()

async def observe_websocket(ws):
    connected.add(ws)
    print("Websocket: opened")
    try:
        async for message in ws:
            result = await transcribe_safe(message)
            await ws.send(json.dumps(result))
    except websockets.ConnectionClosed as e:
        print("Websocket: closed abnormally", e)
    finally:
        print("Websocket: closed")
        connected.remove(ws)

print("Starting server on port 3000")

start_server = websockets.serve(observe_websocket, "0.0.0.0", 3000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

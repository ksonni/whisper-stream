from typing import Set, Any
import asyncio
import websockets

from transcribe import transcribe_safe

import protobufs.transcription_pb2 as pb

connected: Set[websockets.WebSocketServerProtocol] = set()

async def observe_websocket(ws: websockets.WebSocketServerProtocol):
    connected.add(ws)
    print("Websocket: opened", ws.id)
    try:
        async for message in ws:
            await handle_transcription_request(ws, message)
    except websockets.ConnectionClosed as e:
        print("Websocket: closed abnormally", e, ws.id)
    finally:
        print("Websocket: closed", ws.id)
        connected.remove(ws)


async def handle_transcription_request(ws: websockets.WebSocketServerProtocol, msg: str | bytes):
    try:
        request = parse_transcription_request(msg)
    except Exception as e:
        print("Failed to serialize transcription request", e)
        return
    result = await transcribe_safe(request.data)
    await send_respose(ws, pb.TranscriptionResponse(
        serial=request.serial,
        code=200 if result is not None else 500,
        text= result['text'] if result is not None and 'text' in result else None,
    ))

def parse_transcription_request(msg: str | bytes) -> pb.TranscriptionRequest:
    if not isinstance(msg, bytes):
        raise(TypeError("Got unexpected type of websocket message"))
    return pb.TranscriptionRequest.FromString(msg)

async def send_respose(ws: websockets.WebSocketServerProtocol, proto: Any):
    try:
        await ws.send(proto.SerializeToString())
    except Exception as e:
        print("Failed to send message to client", e)

print("Starting server on port 3000")

start_server = websockets.serve(observe_websocket, "0.0.0.0", 3000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

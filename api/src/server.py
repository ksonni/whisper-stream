from typing import Dict
import asyncio
from uuid import UUID
import websockets

from transcription_manager import TranscriptionManager

managers: Dict[UUID, TranscriptionManager] = {}

async def observe_websocket(ws: websockets.WebSocketServerProtocol):
    manager = TranscriptionManager(ws)
    managers[ws.id] =  manager
    print("Websocket: opened", ws.id)
    try:
        async for message in ws:
            await manager.handle_request(message)
    except websockets.ConnectionClosed as e:
        print("Websocket: closed abnormally", e, ws.id)
    finally:
        print("Websocket: closed", ws.id)
        managers.pop(ws.id)

if __name__ ==  '__main__':
    print("Starting server on port 3000")
    start_server = websockets.serve(observe_websocket, "0.0.0.0", 3000)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

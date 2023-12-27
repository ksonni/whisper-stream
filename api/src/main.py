import asyncio
from typing import Dict
from uuid import UUID

import websockets

from config import Config
from services import RequestHandler, WhisperModel

handlers: Dict[UUID, RequestHandler] = {}


async def register_websocket(ws: websockets.WebSocketServerProtocol):
    handler = RequestHandler(ws)
    handlers[ws.id] = handler
    print("Websocket: opened", ws.id)
    try:
        async for message in ws:
            await handler.handle_request(message)
    except websockets.ConnectionClosed as e:
        print("Websocket: closed abnormally", e, ws.id)
    finally:
        print("Websocket: closed", ws.id)
        handlers.pop(ws.id)


if __name__ == '__main__':
    # Load on startup to avoid slowing down 1st request
    print('Loading Whisper model...')
    WhisperModel.load()

    start_server = websockets.serve(register_websocket, "0.0.0.0", Config.server_port)
    asyncio.get_event_loop().run_until_complete(start_server)
    print(f'Server running on port: {Config.server_port}')

    asyncio.get_event_loop().run_forever()

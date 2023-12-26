import asyncio
import websockets

from uuid import UUID
from typing import Dict
from services import RequestHandler
from config import Config

handlers: Dict[UUID, RequestHandler] = {}

async def observe_websocket(ws: websockets.WebSocketServerProtocol):
    handler = RequestHandler(ws)
    handlers[ws.id] =  handler
    print("Websocket: opened", ws.id)
    try:
        async for message in ws:
            await handler.handle_request(message)
    except websockets.ConnectionClosed as e:
        print("Websocket: closed abnormally", e, ws.id)
    finally:
        print("Websocket: closed", ws.id)
        handlers.pop(ws.id)

if __name__ ==  '__main__':
    print(f'Starting server on port: {Config.server_port}')
    start_server = websockets.serve(observe_websocket, "0.0.0.0", Config.server_port)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

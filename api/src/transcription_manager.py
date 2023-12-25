from websockets import WebSocketServerProtocol

from transcribe import transcribe_safe
import protobufs.transcription_pb2 as pb
from typing import Any

class TranscriptionManager:
    def __init__(self, ws: WebSocketServerProtocol):
        self.ws = ws

    async def handle_request(self, msg: str | bytes):
        try:
            request = self.parse_request(msg)
        except Exception as e:
            print("Failed to serialize transcription request", e)
            return
        result = await transcribe_safe(request.data)
        await self.send_respose(pb.TranscriptionResponse(
            serial=request.serial,
            code=200 if result is not None else 500,
            text= result['text'] if result is not None and 'text' in result else None,
        ))

    def parse_request(self, msg: str | bytes) -> pb.TranscriptionRequest:
        if not isinstance(msg, bytes):
            raise(TypeError("Got unexpected type of websocket message"))
        return pb.TranscriptionRequest.FromString(msg)

    async def send_respose(self, proto: Any):
        try:
            await self.ws.send(proto.SerializeToString())
        except Exception as e:
            print("Failed to send message to client", e)
   
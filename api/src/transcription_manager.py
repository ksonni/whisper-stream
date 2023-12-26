from websockets import WebSocketServerProtocol
from multiprocessing import Pool
from multiprocessing.pool import Pool as PoolType

from transcribe import transcribe_safe, TranscribeResult
import protobufs.transcription_pb2 as pb
from typing import Any
import asyncio

# Make this global lazily

class TranscriptionManager:
    
    __shared_pool: PoolType | bool = False 

    def __init__(self, ws: WebSocketServerProtocol):
        self.ws = ws
        self.pool = type(self).__get_shared_pool()
        self.loop = asyncio.get_event_loop()

    async def handle_request(self, msg: str | bytes):
        try:
            request = self.__parse_request(msg)
        except Exception as e:
            print("Failed to serialize transcription request", e)
            return
        print("Handle request happened!!")
        self.pool.apply_async(
            transcribe_safe, 
            args=(request.data,request.serial), 
            callback=self.__handle_transcribe_result,
        )

    async def send_response(self, proto: Any):
        try:
            await self.ws.send(proto.SerializeToString())
        except Exception as e:
            print("Failed to send message to client", e)

    # Helpers 

    def __parse_request(self, msg: str | bytes) -> pb.TranscriptionRequest:
        if not isinstance(msg, bytes):
            raise(TypeError("Got unexpected type of websocket message"))
        return pb.TranscriptionRequest.FromString(msg)

    def __handle_transcribe_result(self, r: TranscribeResult):
        result = r.result
        response = pb.TranscriptionResponse(
            serial=r.serial,
            code=200 if result is not None else 500,
            text= result['text'] if result is not None and 'text' in result else None,
        )
        asyncio.run_coroutine_threadsafe(
            self.send_response(response), self.loop)

    @staticmethod
    def __get_shared_pool() -> PoolType:
        if type(TranscriptionManager.__shared_pool) == PoolType:
            return TranscriptionManager.__shared_pool
        else:
            pool = Pool(processes=1)
            TranscriptionManager.__shared_pool = pool
            return pool

   
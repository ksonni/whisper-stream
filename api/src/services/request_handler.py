import asyncio
import numpy as np
import protobufs.transcription_pb2 as pb
import time

from websockets import WebSocketServerProtocol
from multiprocessing import Pool
from multiprocessing.pool import Pool as PoolType
from .transcribe import transcribe_safe, TranscribeResult
from typing import Any
from config import Config

class RequestHandler:
    
    __shared_pool: PoolType | bool = False 

    def __init__(self, ws: WebSocketServerProtocol):
        self.ws = ws
        self.pool = type(self).__get_shared_pool()
        self.loop = asyncio.get_event_loop()
        self.current_snippet = np.array([], dtype=np.float32)
        self.transcribing = False

    async def handle_request(self, msg: str | bytes):
        try:
            request = self.__parse_request(msg)
        except Exception as e:
            print("Failed to serialize transcription request", e)
            return
        data = np.array(request.data, dtype=np.float32)
        self.current_snippet = np.concatenate((self.current_snippet, data))
        if self.current_snippet.size >= Config.sampling_rate and not self.transcribing:
            self.__transcribe_current_snippet()

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
    
    def __transcribe_current_snippet(self):
        self.transcribing = True
        timestamp = round(time.time() * 1000)
        self.pool.apply_async(
            transcribe_safe, 
            args=(self.current_snippet,timestamp), 
            callback=self.__receive_transcribe_result,
        )

    def __receive_transcribe_result(self, r: TranscribeResult):
        # Relaying result back from the worker thread to the main thread to free up worker
        asyncio.run_coroutine_threadsafe(self.__handle_transcribe_result(r), self.loop)
        
    async def __handle_transcribe_result(self, r: TranscribeResult):
        self.transcribing = False
        result = r.result
        response = pb.TranscriptionResponse(
            timestamp=r.timestamp,
            code=200 if result is not None else 500,
            text= result['text'] if result is not None and 'text' in result else None,
        )
        await self.send_response(response)

    @staticmethod
    def __get_shared_pool() -> PoolType:
        if type(RequestHandler.__shared_pool) == PoolType:
            return RequestHandler.__shared_pool
        else:
            pool = Pool(processes=1)
            RequestHandler.__shared_pool = pool
            return pool

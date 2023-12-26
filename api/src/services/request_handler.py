import asyncio
import numpy as np
import protobufs.transcription_pb2 as pb
import time

from websockets import WebSocketServerProtocol
from multiprocessing import Pool
from multiprocessing.pool import Pool as PoolType
from .transcribe import transcribe_safe, RawTranscriptionResult, decode_raw_result 
from .audio_chunk_manager import AudioChunkManager
from typing import Any
from config import Config

class RequestHandler:
    
    __shared_pool: PoolType | bool = False 

    def __init__(self, ws: WebSocketServerProtocol):
        self.ws = ws
        self.pool = type(self).__get_shared_pool()
        self.loop = asyncio.get_event_loop()
        self.chunk_manager = AudioChunkManager()
        self.transcribing = False

    async def handle_request(self, msg: str | bytes):
        try:
            request = self.__parse_request(msg)
        except Exception as e:
            print("Failed to serialize transcription request", e)
            return
        data = np.array(request.data, dtype=np.float32)
        self.chunk_manager.append_audio(data)
        if self.chunk_manager.buffer.size >= Config.sampling_rate and not self.transcribing:
            self.__transcribe_current_buffer()

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
    
    def __transcribe_current_buffer(self):
        self.transcribing = True
        timestamp = round(time.time() * 1000)
        self.pool.apply_async(
            transcribe_safe, 
            args=(self.chunk_manager.buffer,timestamp), 
            callback=self.__receive_transcribe_result,
            error_callback=self.__receive_transcribe_error
        )

    def __receive_transcribe_result(self, raw: RawTranscriptionResult):
        # Relaying result back from the worker thread to the main thread to free up worker
        asyncio.run_coroutine_threadsafe(self.__handle_transcribe_result(raw), self.loop)

    def __receive_transcribe_error(self, err: Any):
        print("An unexpected occured when transcribing", err)
        asyncio.run_coroutine_threadsafe(
            self.__handle_transcribe_result(RawTranscriptionResult(None, None)), self.loop)

    async def __handle_transcribe_result(self, raw: RawTranscriptionResult):
        result = decode_raw_result(raw)
        self.chunk_manager.append_result(result)
        self.transcribing = False
        await self.send_response(result)

    @staticmethod
    def __get_shared_pool() -> PoolType:
        if type(RequestHandler.__shared_pool) == PoolType:
            return RequestHandler.__shared_pool
        else:
            pool = Pool(processes=1)
            RequestHandler.__shared_pool = pool
            return pool

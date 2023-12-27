import asyncio
import time
from multiprocessing import Pool
from multiprocessing.pool import Pool as PoolType
from typing import Any
from uuid import uuid4 as uuid

import numpy as np
from websockets import WebSocketServerProtocol

import protobufs.transcription_pb2 as pb
from config import Config
from .audio_chunk_manager import AudioChunkManager
from .transcribe import transcribe_safe, TranscriptionParams, TranscriptionResult


class RequestHandler:
    __shared_pool: PoolType | bool = False

    def __init__(self, ws: WebSocketServerProtocol):
        self.ws = ws
        self.pool = type(self).__get_shared_pool()
        self.loop = asyncio.get_event_loop()
        self.chunk_manager = AudioChunkManager()
        self.transcribing = False
        self.last_transcribe_time: float = 0

    async def handle_request(self, msg: str | bytes):
        try:
            request = self.__parse_request(msg)
        except Exception as e:
            print("Failed to serialize transcription request", e)
            return
        data = np.array(request.data, dtype=np.float32)
        self.chunk_manager.append_audio_chunk(data)
        if self.can_transcribe:
            self.__transcribe_current_buffer()

    async def send_response(self, proto: Any):
        try:
            await self.ws.send(proto.SerializeToString())
        except Exception as e:
            print("Failed to send message to client", e)

    # Helpers

    def __transcribe_current_buffer(self):
        self.transcribing = True
        self.chunk_manager.prune_chunks()
        if not self.chunk_manager.has_min_buffer:
            self.transcribing = False
            return
        params = TranscriptionParams(uuid(), self.chunk_manager.copy_buffer())
        self.last_transcribe_time = time.time()
        self.pool.apply_async(
            transcribe_safe,
            args=(params,),
            callback=self.__receive_transcribe_result,
            error_callback=self.__receive_transcribe_error
        )

    def __receive_transcribe_result(self, raw: TranscriptionResult):
        asyncio.run_coroutine_threadsafe(self.__handle_transcribe_result(raw), self.loop)

    def __receive_transcribe_error(self, err: Any):
        # This indicates a programming error - transcribe_safe should handle all exceptions
        raise AssertionError("A fatal error occurred when receiving transcription result", err)

    async def __handle_transcribe_result(self, result: TranscriptionResult):
        if not result.error:
            self.chunk_manager.append_transcription_result(result)
        self.transcribing = False
        await self.send_response(pb.TranscriptionResponse(
            buffer_start=result.buffer_start,
            buffer_end=result.buffer_end,
            code=200 if not result.error else 500,
            chunks=map(lambda c: pb.TranscriptionChunk(
                text=c.text,
                start_time=c.start_time,
                end_time=c.end_time
            ), result.chunks)
        ))

    @property
    def can_transcribe(self) -> bool:
        return (self.chunk_manager.has_min_buffer and not self.transcribing and
                (time.time() - self.last_transcribe_time >= 60 / Config.max_transcriptions_pm))

    @staticmethod
    def __parse_request(msg: str | bytes) -> pb.TranscriptionRequest:
        if not isinstance(msg, bytes):
            raise (TypeError("Got unexpected type of websocket message"))
        return pb.TranscriptionRequest.FromString(msg)

    @staticmethod
    def __get_shared_pool() -> PoolType:
        if isinstance(RequestHandler.__shared_pool, PoolType):
            return RequestHandler.__shared_pool
        else:
            pool = Pool(processes=1)
            RequestHandler.__shared_pool = pool
            return pool

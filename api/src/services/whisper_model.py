from abc import ABC, abstractmethod
from typing import Dict

import numpy as np
import torch
import whisper
from transformers import pipeline, Pipeline
from whisper import Whisper

from config import Config, WhisperImpl


class Model(ABC):
    @abstractmethod
    def transcribe(self, buffer: np.ndarray) -> Dict:
        pass

    @abstractmethod
    def load(self):
        pass


class TransformersImpl(Model):
    def __init__(self):
        self.__pipeline: Pipeline | bool = False

    def transcribe(self, buffer: np.ndarray) -> Dict:
        return self.__load_pipeline()(buffer, chunk_length_s=10, return_timestamps=True)

    def load(self):
        self.__load_pipeline()

    def __load_pipeline(self) -> Pipeline:
        if isinstance(self.__pipeline, Pipeline):
            return self.__pipeline
        pipe = pipeline(
            "automatic-speech-recognition",
            model=f'openai/whisper-{Config.whisper_model}',
            torch_dtype=torch.float16,
            device="cuda:0" if torch.cuda.is_available() else "mps",
        )
        self.__pipeline = pipe
        return pipe


class OpenAIImpl(Model):
    def __init__(self):
        self.__model: Whisper | bool = False

    def transcribe(self, buffer: np.ndarray) -> Dict:
        # Reformat to make it align with the transformers output
        out = self.__load_model().transcribe(buffer, no_speech_threshold=0.4)
        out["segments"] = filter(
            lambda c : c["no_speech_prob"] is None or c["no_speech_prob"] < 0.4, out["segments"])
        return {"chunks": map(lambda s: {
            'text': s['text'],
            'timestamp': (s['start'], s['end']),
        }, out["segments"])}

    def load(self):
        self.__load_model()

    def __load_model(self) -> Whisper:
        if isinstance(self.__model, Whisper):
            return self.__model
        model = whisper.load_model(Config.whisper_model)
        self.__model = model
        return model


def _make_model() -> Model:
    match Config.whisper_implementation:
        case WhisperImpl.OpenAI:
            return OpenAIImpl()
        case WhisperImpl.Transformers:
            return TransformersImpl()


WhisperModel = _make_model()

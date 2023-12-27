from dataclasses import dataclass


@dataclass
class __Config:
    # Sampling rate the client is expected to use
    sampling_rate = 16_000

    # Number of times chunks should produce the same text for them to be considered "stable" & then pruned
    min_stable_transcriptions = 2

    # Port on which the server runs
    server_port = 3000

    # Max transcriptions per minute per session
    max_transcriptions_pm = 80


Config = __Config()

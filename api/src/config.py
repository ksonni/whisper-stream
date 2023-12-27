from dataclasses import dataclass


@dataclass
class __Config:
    # Sampling rate the client is expected to use
    sampling_rate = 16_000

    # Port on which the server runs
    server_port = 3000


Config = __Config()

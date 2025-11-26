import numpy as np
from ml.stt_whisper import transcribe_and_parse_from_audio_array


def process_command(audio: np.ndarray, sr: int):
    return transcribe_and_parse_from_audio_array(audio, sr)

import numpy as np
from ml.authenticate_voice import (
    verify_from_audio_array,
    generate_challenge_word,
    get_voiceprint_path
)
import os


def get_challenge(user_id: str):
    if not os.path.exists(get_voiceprint_path(user_id)):
        return {"has_voiceprint": False, "word": None}

    return {"has_voiceprint": True, "word": generate_challenge_word()}


def verify_voice(user_id: str, audio: np.ndarray):
    return verify_from_audio_array(user_id, audio)

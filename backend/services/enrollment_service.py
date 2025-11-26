import numpy as np
from ml.enroll_voice import enroll_from_audio_array


def enroll_user_voice(user_id: str, audio: np.ndarray):
    return enroll_from_audio_array(user_id, audio)

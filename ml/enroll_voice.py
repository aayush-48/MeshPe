import os
os.environ["RESEMBLYZER_FORCE_NO_VAD"] = "1"

import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav

encoder = VoiceEncoder()
SAMPLE_RATE = 16000


def get_voiceprint_path(user_id: str):
    base = os.path.join("ml", "models", "stored_voiceprints")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, f"{user_id}.npy")


def enroll_from_audio_array(user_id: str, audio):
    wav = preprocess_wav(audio, SAMPLE_RATE)
    emb = encoder.embed_utterance(wav)

    path = get_voiceprint_path(user_id)
    np.save(path, emb)
    return path

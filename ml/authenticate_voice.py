import os
import numpy as np
from numpy.linalg import norm
from resemblyzer import VoiceEncoder, preprocess_wav
import random

encoder = VoiceEncoder()
SAMPLE_RATE = 16000

WORDS = ["apple", "neon", "matrix", "secure", "galaxy", "mesh", "ocean", "binary"]


def get_voiceprint_path(user_id: str):
    return os.path.join("ml", "models", "stored_voiceprints", f"{user_id}.npy")


def generate_challenge_word():
    return random.choice(WORDS)


def verify_from_audio_array(user_id: str, audio, threshold=0.5):
    path = get_voiceprint_path(user_id)
    if not os.path.exists(path):
        return {"exists": False, "verified": False, "score": None}

    stored = np.load(path)

    wav = preprocess_wav(audio, SAMPLE_RATE)
    live = encoder.embed_utterance(wav)

    score = float(np.dot(stored, live) / (norm(stored) * norm(live) + 1e-9))
    print(f"Voice verification score for {user_id}: {score} (threshold {threshold})")

    return {
        "exists": True,
        "verified": score >= threshold,
        "score": score
    }

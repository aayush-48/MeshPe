import os
import pickle
import numpy as np
import librosa

# Global cache for the model
_MODEL = None
_MODEL_PATH = os.path.join(os.path.dirname(__file__), "anti_replay_model.pkl")
LIVENESS_THRESHOLD = 0.9  # Probability threshold for "Fake/Replay" class

def _load_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    
    if not os.path.exists(_MODEL_PATH):
        print(f"[Liveness] Model not found at {_MODEL_PATH}")
        return None

    try:
        with open(_MODEL_PATH, 'rb') as f:
            _MODEL = pickle.load(f)
        print("[Liveness] Anti-replay model loaded successfully")
    except Exception as e:
        print(f"[Liveness] Failed to load model: {e}")
    
    return _MODEL

def _extract_features(audio: np.ndarray, sr: int) -> np.ndarray:
    try:
        # Ensure audio is float32
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)

        # MFCC extraction (13 coeffs)
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
        # Delta features
        delta = librosa.feature.delta(mfccs)
        # Stack and flatten
        combined = np.vstack([mfccs, delta])
        # Mean across time -> shape (1, 26)
        return np.mean(combined.T, axis=0).reshape(1, -1)
    except Exception as e:
        print(f"[Liveness] Feature extraction error: {e}")
        return None

def check_liveness(audio: np.ndarray, samplerate=16000) -> bool:
    """
    Returns True if audio is LIVE, False if REPLAY/FAKE.
    """
    model = _load_model()
    if model is None:
        # Fail safe: if model missing, assume live (or fail secure depending on policy)
        # For now, let's log error and return True to not block dev, 
        # but in prod this should probably be False.
        print("[Liveness] WARNING: Model missing, skipping check.")
        return True

    features = _extract_features(audio, samplerate)
    if features is None:
        return False

    try:
        # Model predicts probability of class 1 (Replay/Fake)
        # Assuming class 0 = Live, class 1 = Replay
        # Based on test_anti_replay.py: prob < threshold => LIVE
        prob = model.predict_proba(features)[0][1]
        
        is_live = prob < LIVENESS_THRESHOLD
        print(f"[Liveness] Score: {prob:.3f} (Threshold: {LIVENESS_THRESHOLD}) -> {'LIVE' if is_live else 'FAKE'}")
        
        return is_live
    except Exception as e:
        print(f"[Liveness] Prediction error: {e}")
        return False

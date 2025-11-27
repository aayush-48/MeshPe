import pathlib
import pickle
import numpy as np
import librosa
import io
import sys
from pathlib import Path

MODELS_DIR = pathlib.Path("models")  # Change to your actual model directory if needed
TEST_AUDIO_PATH = "sample.wav"       # Change this to your test audio file

class Config:
    MODELS_DIR = MODELS_DIR
    LIVENESS_THRESHOLD = 0.5 # Change as per your config or experiment

# def load_anti_replay_model():
#     model_path = r'C:\Users\Asmiya\Desktop\Mini-Proj\backend\models\anti_replay_model.pkl'
#     if not model_path.exists():
#         print("Anti-replay model not found at:", model_path)
#         return None
#     with open(model_path, 'rb') as f:
#         model = pickle.load(f)
#     print("✓ Anti-replay classifier loaded")
#     return model
def load_anti_replay_model():
    model_path = Path(r'C:\Users\Asmiya\Desktop\Mini-Proj\backend\models\anti_replay_model.pkl')  # Ensure this is correct
    if not model_path.exists():
        print("Anti-replay model not found at:", model_path)
        return None
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    print("✓ Anti-replay classifier loaded")
    return model

def extract_mfcc(audio_path: str) -> np.ndarray:
    try:
        y, sr = librosa.load(audio_path, sr=16000)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        delta = librosa.feature.delta(mfccs)
        combined = np.vstack([mfccs, delta])
        return np.mean(combined.T, axis=0).reshape(1, -1)
    except Exception as e:
        print(f"MFCC extraction error: {e}")
        return np.zeros((1, 26))

def check_liveness(audio_path: str):
    model = load_anti_replay_model()
    if not model:
        print("Model not loaded, cannot proceed.")
        return
    features = extract_mfcc(audio_path)
    try:
        prob = model.predict_proba(features)[0][1]
        print(f"Liveness Probability: {prob:.3f}")
        if prob < Config.LIVENESS_THRESHOLD:
            print("Result: LIVE audio detected")
        else:
            print("Result: REPLAYED or SYNTHETIC audio detected")
    except Exception as e:
        print(f"Liveness check error: {e}")

if __name__ == "__main__":
    test_audio = sys.argv[1] if len(sys.argv) > 1 else TEST_AUDIO_PATH
    check_liveness(test_audio)

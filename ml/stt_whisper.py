import numpy as np
from faster_whisper import WhisperModel
from .nlp_parse import extract_amount, extract_action, extract_receiver

_model = WhisperModel("base", device="cpu", compute_type="int8")


import scipy.signal

def transcribe_and_parse_from_audio_array(audio: np.ndarray, samplerate: int = 16000):
    # Resample to 16000 Hz if needed (Whisper expects 16k)
    if samplerate != 16000:
        num_samples = int(len(audio) * 16000 / samplerate)
        print(f"Resampling audio from {samplerate}Hz to 16000Hz...")
        audio = scipy.signal.resample(audio, num_samples)

    audio = audio.astype("float32")
    audio = audio / (np.max(np.abs(audio)) + 1e-8)

    segments, _ = _model.transcribe(audio)
    text = " ".join(seg.text for seg in segments).strip().lower()

    action = extract_action(text)
    amount = extract_amount(text)
    receiver = extract_receiver(text)

    return {
        "raw_text": text,
        "action": action,
        "amount": amount,
        "receiver": receiver
    }

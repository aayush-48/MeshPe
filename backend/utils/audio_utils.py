import io
from typing import Tuple

import numpy as np
import soundfile as sf
import av  # PyAV - robust container/codec support (e.g. webm/opus)


def _load_with_soundfile(data: bytes) -> Tuple[np.ndarray, int]:
    audio, sr = sf.read(io.BytesIO(data), dtype="float32")
    if audio.ndim > 1:
        audio = audio[:, 0]
    return audio, sr


def _load_with_pyav(data: bytes) -> Tuple[np.ndarray, int]:
    """
    Fallback loader using PyAV for formats soundfile can't handle (e.g. audio/webm).
    Returns mono float32 numpy array and samplerate.
    """
    import tempfile
    import os
    
    # Write to a temporary file to ensure PyAV can probe/seek correctly
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    try:
        frames = []
        sr = 48000 # Default fallback
        
        with av.open(tmp_path) as container:
            audio_stream = next((s for s in container.streams if s.type == "audio"), None)
            if audio_stream is None:
                raise RuntimeError("No audio stream found in container")

            sr = audio_stream.rate
            print(f"PyAV stream detected: {audio_stream.codec_context.name}, rate={sr}")

            for frame in container.decode(audio_stream):
                frame_arr = frame.to_ndarray()
                # PyAV often returns (channels, samples) for planar formats (like fltp).
                # We want (samples, channels) for concatenation.
                if frame_arr.ndim == 2 and frame_arr.shape[0] < frame_arr.shape[1]:
                    frame_arr = frame_arr.T
                frames.append(frame_arr)
            
        print(f"PyAV decoded {len(frames)} frames")

        if not frames:
            raise RuntimeError("No audio frames decoded")

        audio = np.concatenate(frames, axis=0)
        
        if audio.ndim == 1:
            mono = audio
        else:
            mono = audio.mean(axis=1)
            
        return mono.astype("float32"), sr
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def load_audio_mono_from_bytes(data: bytes) -> Tuple[np.ndarray, int]:
    """
    Load audio bytes into a mono float32 numpy array and samplerate.
    Tries soundfile first; if that fails (e.g. for webm/opus), falls back to PyAV.

    Frontend currently records audio using MediaRecorder with mime-type 'audio/webm'
    (see frontend/src/utils/audioUtils.ts). soundfile often can't decode webm/opus,
    so this fallback is required.
    """
    try:
        print("Attempting to load with soundfile...")
        audio, sr = _load_with_soundfile(data)
        print(f"Soundfile success: {audio.shape} @ {sr}")
        return audio, sr
    except Exception as e:
        print(f"Soundfile failed: {e}")
        print("Attempting to load with PyAV...")
        audio, sr = _load_with_pyav(data)
        print(f"PyAV success: {audio.shape} @ {sr}")
        return audio, sr


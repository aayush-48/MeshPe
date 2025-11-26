from fastapi import APIRouter, UploadFile, File, HTTPException
import numpy as np
from backend.services.stt_service import process_command
from backend.utils.audio_utils import load_audio_mono_from_bytes

router = APIRouter()


@router.post("/command")
async def stt_command(file: UploadFile = File(...)):
    try:
        data = await file.read()
        audio, sr = load_audio_mono_from_bytes(data)
        return process_command(audio, sr)
    except Exception:
        raise HTTPException(status_code=400, detail="STT failed")

from fastapi import APIRouter, UploadFile, File, HTTPException
import numpy as np
from backend.services.enrollment_service import enroll_user_voice
from backend.utils.audio_utils import load_audio_mono_from_bytes

router = APIRouter()


@router.post("/{user_id}")
async def enroll(user_id: str, file: UploadFile = File(...)):
    try:
        data = await file.read()
        audio, sr = load_audio_mono_from_bytes(data)
        enroll_user_voice(user_id, audio)
        return {"status": "ok"}
    except Exception:
        raise HTTPException(status_code=400, detail="Enrollment failed")

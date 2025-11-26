from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
import soundfile as sf
from backend.services.auth_service import get_challenge, verify_voice
from backend.services.enrollment_service import enroll_user_voice
from backend.storage.user_store import create_or_update_user, get_user, add_contact, list_contacts
from backend.utils.audio_utils import load_audio_mono_from_bytes

router = APIRouter()


# ----- Existing low-level endpoints (kept for compatibility) -----


@router.get("/challenge/{user_id}")
async def challenge(user_id: str):
    return get_challenge(user_id)


@router.post("/verify/{user_id}")
async def verify(user_id: str, file: UploadFile = File(...)):
    try:
        data = await file.read()
        audio, sr = load_audio_mono_from_bytes(data)
        return verify_voice(user_id, audio)
    except Exception:
        raise HTTPException(status_code=400, detail="Verification failed")


# ----- Frontend-friendly auth & user endpoints -----


@router.post("/signup")
async def signup(
    name: str = Form(...),
    phone: str = Form(...),
    language: str = Form("english"),
    audio_1: UploadFile = File(...),
):
    """
    Endpoint used by the frontend SignupScreen.
    Stores basic user info and enrolls a voiceprint from the first audio sample.
    """
    try:
        # Use first audio sample for enrollment
        data = await audio_1.read()
        audio, sr = load_audio_mono_from_bytes(data)

        user_id = phone
        enroll_user_voice(user_id, audio)
        user = create_or_update_user(user_id=user_id, name=name, phone=phone, language=language)

        return {"success": True, "data": {"user": user}, "message": "Signup successful"}
    except Exception as e:
        # Return structured error instead of HTTP 400 so frontend can show it
        print("Signup failed:", e)
        return {"success": False, "error": str(e)}


class LoginStartReq(BaseModel):
    user_id: str


@router.post("/login/start")
async def login_start(payload: LoginStartReq):
    """
    Start login: frontend sends { user_id } (currently phone).
    Returns a challenge word if a voiceprint exists.
    """
    user_id = payload.user_id
    info = get_challenge(user_id)
    if not info.get("has_voiceprint"):
        return {"success": False, "error": "No enrolled voice for this user"}

    return {"success": True, "data": {"challenge": info.get("word")}}


@router.post("/login/verify")
async def login_verify(
    user_id: str = Form(...),
    audio: UploadFile = File(...),
    language: str = Form("english"),
):
    """
    Verify login using a recorded challenge phrase.
    Frontend sends FormData with user_id, audio, language.
    """
    try:
        data = await audio.read()
        audio_arr, sr = load_audio_mono_from_bytes(data)

        result = verify_voice(user_id, audio_arr)
        if not result.get("exists"):
            return {"success": False, "error": "No enrolled voice for this user"}
        if not result.get("verified"):
            return {"success": False, "error": "Voice verification failed"}

        user = get_user(user_id)
        if not user:
            # Create a minimal user record if not present
            user = create_or_update_user(user_id=user_id, name=user_id, phone=user_id, language=language)

        return {"success": True, "data": {"user": user}}
    except Exception:
        raise HTTPException(status_code=400, detail="Login verification failed")


@router.post("/logout")
async def logout():
    """
    Stateless logout (frontend clears local storage).
    """
    return {"success": True, "message": "Logged out"}


class ContactReq(BaseModel):
    contact_name: str
    contact_id: str


@router.post("/contacts/add")
async def contacts_add(user_id: str, payload: ContactReq):
    contacts = add_contact(user_id, payload.contact_name, payload.contact_id)
    return {"success": True, "data": {"contacts": contacts}}


@router.get("/contacts/list")
async def contacts_list(user_id: str):
    contacts = list_contacts(user_id)
    return {"success": True, "data": {"contacts": contacts}}

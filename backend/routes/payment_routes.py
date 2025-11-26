from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
import numpy as np

from backend.services.payment_service import create_packet
from backend.services.stt_service import process_command
from backend.services.encryption_service import encrypt_packet
from backend.services.auth_service import verify_voice
from backend.services.mesh_service import send_to_mesh
from backend.storage.user_store import get_user, list_contacts
from backend.utils.audio_utils import load_audio_mono_from_bytes
from ml.liveness import check_liveness

router = APIRouter()


class PaymentReq(BaseModel):
    sender_id: str
    sender_name: str
    sender_account: str
    receiver_name: str
    receiver_account: str
    amount: int
    ttl: int = 60


@router.post("/packet")
async def packet(payload: PaymentReq):
    return create_packet(
        payload.sender_id,
        payload.sender_name,
        payload.sender_account,
        payload.receiver_name,
        payload.receiver_account,
        payload.amount,
        payload.ttl,
    )


@router.post("/initiate")
async def initiate_payment(
    user_id: str = Form(...),
    audio: UploadFile = File(...),
    language: str = Form("english"),
):
    """
    Step 1: user speaks a payment command, e.g. "pay bob 100 rupees".
    We first authenticate + liveness-check this command audio,
    then run STT+NLP to extract receiver and amount and return a summary.
    """
    try:
        data = await audio.read()
        audio_arr, sr = load_audio_mono_from_bytes(data)

        # First-level voice auth + liveness on the command itself
        verify_result = verify_voice(user_id, audio_arr)
        if not verify_result.get("exists"):
            return {"success": False, "error": "No enrolled voice for this user"}
        if not verify_result.get("verified"):
            return {"success": False, "error": "Voice verification failed for command"}

        if not check_liveness(audio_arr):
            return {"success": False, "error": "Liveness check failed for command"}

        # STT + NLP
        cmd = process_command(audio_arr, sr)
        # Debug log so we can see what Whisper+NLP extracted
        print(f"Received audio bytes: {len(data)}")
        print(f"Audio array shape: {audio_arr.shape}, Max amp: {np.max(np.abs(audio_arr))}")
        print("Payment command parsed:", cmd)
        action = cmd.get("action")
        amount = cmd.get("amount")
        receiver_text = cmd.get("receiver")

        if action not in ("pay", "send", "transfer") or amount is None or not receiver_text:
            raw = cmd.get("raw_text", "")
            return {
                "success": False,
                "error": f"Could not parse payment command. Heard: '{raw}'",
            }

        user = get_user(user_id)
        if not user:
            raise HTTPException(status_code=400, detail="Unknown user")

        contacts = list_contacts(user_id)
        receiver_text_lower = receiver_text.lower()
        matched_contact = None
        for c in contacts:
            if c.get("name", "").lower().startswith(receiver_text_lower):
                matched_contact = c
                break
        if not matched_contact:
            return {
                "success": False,
                "error": f"Receiver '{receiver_text}' not found in contacts",
            }

        payment_info = {
            "receiver_name": matched_contact["name"],
            "amount": amount,
            "currency": "INR",
        }

        return {
            "success": True,
            "data": {
                "payment_info": payment_info,
                "raw_text": cmd.get("raw_text"),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Payment initiation failed: {str(e)}")


@router.post("/confirm")
async def confirm_payment(
    user_id: str = Form(...),
    audio: UploadFile = File(...),
    receiver_name: str = Form(...),
    amount: int = Form(...),
    language: str = Form("english"),
):
    """
    Step 2: user says "yes" to confirm.
    We re-verify voice against enrolled embedding and run liveness,
    then create and encrypt the packet and send it to the bank (mocked),
    finally returning payment info to the frontend.
    """
    try:
        data = await audio.read()
        audio_arr, sr = load_audio_mono_from_bytes(data)

        # Voice re-verification
        verify_result = verify_voice(user_id, audio_arr)
        if not verify_result.get("exists"):
            return {"success": False, "error": "No enrolled voice for this user"}
        if not verify_result.get("verified"):
            return {"success": False, "error": "Voice verification failed during confirmation"}

        # Liveness check
        if not check_liveness(audio_arr):
            return {"success": False, "error": "Liveness check failed"}

        user = get_user(user_id)
        if not user:
            raise HTTPException(status_code=400, detail="Unknown user")

        contacts = list_contacts(user_id)
        receiver_contact = None
        for c in contacts:
            if c.get("name", "").lower() == receiver_name.lower():
                receiver_contact = c
                break
        if not receiver_contact:
            return {
                "success": False,
                "error": f"Receiver '{receiver_name}' not found in contacts",
            }

        sender_account = f"ACC-{user_id}"
        receiver_account = f"ACC-{receiver_contact['id']}"

        packet = create_packet(
            user_id,
            user.get("name", user_id),
            sender_account,
            receiver_contact["name"],
            receiver_account,
            int(amount),
        )

        encrypted = encrypt_packet(packet)

        # Mock Bluetooth/mesh by directly "sending" to bank server
        forwarded = send_to_mesh(encrypted)
        if not forwarded:
            return {"success": False, "error": "Failed to forward packet to bank server"}

        payment_info = {
            "receiver_name": receiver_contact["name"],
            "amount": int(amount),
            "currency": "INR",
        }

        return {
            "success": True,
            "data": {
                "payment_info": payment_info,
            },
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Payment confirmation failed")

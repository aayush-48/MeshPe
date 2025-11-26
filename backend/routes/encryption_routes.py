from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.encryption_service import encrypt_packet
from backend.services.mesh_service import send_to_mesh

router = APIRouter()


class PacketModel(BaseModel):
    packet_id: str
    sender_id: str
    sender_name: str
    sender_account: str
    receiver_name: str
    receiver_account: str
    amount: int
    ttl: int
    timestamp: str


@router.post("/seal-send")
async def seal_and_send(payload: PacketModel):
    try:
        encrypted = encrypt_packet(payload.dict())
        forwarded = send_to_mesh(encrypted)
        return {"encrypted": encrypted, "forwarded": forwarded}
    except Exception:
        raise HTTPException(status_code=400, detail="Encryption failed")

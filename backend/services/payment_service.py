import uuid
from backend.utils.time_utils import get_current_timestamp


def create_packet(sender_id, sender_name, sender_acc, receiver_name, receiver_acc, amount, ttl=60):
    return {
        "packet_id": str(uuid.uuid4()),
        "sender_id": sender_id,
        "sender_name": sender_name,
        "sender_account": sender_acc,
        "receiver_name": receiver_name,
        "receiver_account": receiver_acc,
        "amount": amount,
        "ttl": ttl,
        "timestamp": get_current_timestamp()
    }

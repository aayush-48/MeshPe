import json
from backend.crypto.aes_utils import aes_encrypt
from backend.crypto.rsa_utils import rsa_encrypt
from backend.crypto.key_loader import load_bank_public_key

def encrypt_packet(packet: dict):
    data = json.dumps(packet).encode()
    aes_key, iv, ciphertext, tag = aes_encrypt(data)

    print("\n--- [ENCRYPTION START] ---")
    print(f"Original Data: {data}")
    print(f"Generated AES Key: {aes_key.hex()}")
    print(f"AES IV: {iv.hex()}")
    print(f"Ciphertext: {ciphertext.hex()}")
    print(f"Auth Tag: {tag.hex()}")

    rsa_key = load_bank_public_key()
    encrypted_key = rsa_encrypt(rsa_key, aes_key)
    print(f"Encrypted AES Key (RSA): {encrypted_key.hex()}")
    print("--- [ENCRYPTION END] ---\n")

    return {
        "encrypted_key": encrypted_key.hex(),
        "iv": iv.hex(),
        "ciphertext": ciphertext.hex(),
        "tag": tag.hex(),
        "timestamp": packet["timestamp"],
        "packet_id": packet["packet_id"]
    }

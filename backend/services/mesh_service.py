from backend.crypto.bank_keys import load_bank_private_key
from backend.crypto.aes_utils import AES
from Crypto.Cipher import AES as CryptoAES
from binascii import unhexlify
from Crypto.Cipher import PKCS1_OAEP


def _rsa_decrypt_with_bank_private_key(encrypted_key_hex: str) -> bytes:
    private_key = load_bank_private_key()
    cipher = PKCS1_OAEP.new(private_key)
    return cipher.decrypt(unhexlify(encrypted_key_hex))


def _aes_decrypt_packet(aes_key: bytes, iv_hex: str, ciphertext_hex: str, tag_hex: str) -> bytes:
    iv = unhexlify(iv_hex)
    ciphertext = unhexlify(ciphertext_hex)
    tag = unhexlify(tag_hex)
    cipher = CryptoAES.new(aes_key, CryptoAES.MODE_GCM, nonce=iv)
    return cipher.decrypt_and_verify(ciphertext, tag)


def send_to_mesh(encrypted_packet: dict) -> bool:
    """
    Dummy bank server: decrypts the received packet using the bank's
    private RSA key and the AES session key, and logs the result.
    In a real system this would credit/debit accounts, etc.
    """
    try:
        print("\n--- [DECRYPTION START (BANK SIDE)] ---")
        print(f"Received Encrypted Key: {encrypted_packet['encrypted_key']}")
        
        # 1) Recover AES session key with bank's private RSA key
        aes_key = _rsa_decrypt_with_bank_private_key(encrypted_packet["encrypted_key"])
        print(f"Decrypted AES Key: {aes_key.hex()}")

        # 2) Decrypt packet JSON with AES-GCM
        plaintext = _aes_decrypt_packet(
            aes_key,
            encrypted_packet["iv"],
            encrypted_packet["ciphertext"],
            encrypted_packet["tag"],
        )
        print(f"Decrypted Payload (Plaintext): {plaintext}")
        print("--- [DECRYPTION END] ---\n")

        # 3) For demo, just print/log the JSON payload
        from json import loads

        packet = loads(plaintext.decode("utf-8"))
        # You can add real business logic here; for now we just acknowledge.
        print("Dummy bank server received packet:", packet)
        return True
    except Exception as e:
        print("Dummy bank server failed to process packet:", e)
        return False

from Crypto.PublicKey import RSA
from backend.crypto.bank_keys import load_bank_public_key as _auto_load_pub


def load_bank_public_key() -> RSA.RsaKey:
    """
    Backwards-compatible wrapper used by encryption_service.
    Ensures keys exist and returns the bank's public key.
    """
    return _auto_load_pub()

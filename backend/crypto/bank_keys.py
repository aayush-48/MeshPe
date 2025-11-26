from pathlib import Path
from Crypto.PublicKey import RSA

BASE_DIR = Path(__file__).resolve().parent.parent
BANK_PRIV_PATH = BASE_DIR / "bank_private.pem"
BANK_PUB_PATH = BASE_DIR / "bank_public.pem"


def ensure_bank_keys() -> None:
    """
    Ensure an RSA keypair exists for the dummy bank server.
    If missing, generate a new 2048-bit key and store it in PEM files.
    """
    if BANK_PRIV_PATH.exists() and BANK_PUB_PATH.exists():
        return

    key = RSA.generate(2048)
    BANK_PRIV_PATH.write_bytes(key.export_key("PEM"))
    BANK_PUB_PATH.write_bytes(key.publickey().export_key("PEM"))


def load_bank_private_key() -> RSA.RsaKey:
    ensure_bank_keys()
    return RSA.import_key(BANK_PRIV_PATH.read_bytes())


def load_bank_public_key() -> RSA.RsaKey:
    ensure_bank_keys()
    return RSA.import_key(BANK_PUB_PATH.read_bytes())



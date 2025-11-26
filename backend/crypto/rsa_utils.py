from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


def rsa_encrypt(public_key: RSA.RsaKey, data: bytes) -> bytes:
    cipher = PKCS1_OAEP.new(public_key)
    return cipher.encrypt(data)

import os
from Crypto.Cipher import AES


def aes_encrypt(plaintext: bytes):
    key = os.urandom(32)
    iv = os.urandom(12)

    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)

    return key, iv, ciphertext, tag

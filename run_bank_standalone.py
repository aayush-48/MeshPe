import socket
import json
import logging
import os
import sys
from binascii import unhexlify

# Dependencies: pip install pycryptodome
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES as CryptoAES
from Crypto.Cipher import PKCS1_OAEP

# --- CONFIGURATION ---
BANK_KEY_FILE = "bank_private.pem"
RFCOMM_CHANNEL = 4  # Port for Bluetooth communication

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("BankNode")

# --- CRYPTO UTILS ---

def load_private_key():
    if not os.path.exists(BANK_KEY_FILE):
        logger.error(f"CRITICAL: '{BANK_KEY_FILE}' not found!")
        logger.error("Please copy 'bank_private.pem' from the Sender device to this folder.")
        return None
    with open(BANK_KEY_FILE, "rb") as f:
        return RSA.import_key(f.read())

def decrypt_rsa(encrypted_hex: str, private_key):
    cipher = PKCS1_OAEP.new(private_key)
    return cipher.decrypt(unhexlify(encrypted_hex))

def decrypt_aes(aes_key: bytes, iv_hex: str, ciphertext_hex: str, tag_hex: str):
    iv = unhexlify(iv_hex)
    ciphertext = unhexlify(ciphertext_hex)
    tag = unhexlify(tag_hex)
    cipher = CryptoAES.new(aes_key, CryptoAES.MODE_GCM, nonce=iv)
    return cipher.decrypt_and_verify(ciphertext, tag)

# --- BLUETOOTH SERVER (RFCOMM) ---

def process_packet(data: str):
    """
    Decrypts and processes the received packet.
    """
    logger.info("\n--- [BANK NODE: PROCESSING PACKET] ---")
    
    private_key = load_private_key()
    if not private_key:
        return

    try:
        packet = json.loads(data)
        logger.info(f"Received Encrypted Key: {packet['encrypted_key'][:20]}...")
        
        # 1) Recover AES session key
        aes_key = decrypt_rsa(packet["encrypted_key"], private_key)
        logger.info(f"Decrypted AES Key: {aes_key.hex()}")

        # 2) Decrypt packet JSON
        plaintext = decrypt_aes(
            aes_key,
            packet["iv"],
            packet["ciphertext"],
            packet["tag"],
        )
        logger.info(f"Decrypted Payload (Plaintext): {plaintext}")

        # 3) Parse JSON
        payload = json.loads(plaintext.decode("utf-8"))
        logger.info(f"PAYMENT RECEIVED: {payload}")
        logger.info("--- [TRANSACTION SUCCESS] ---\n")
        
    except Exception as e:
        logger.error(f"Failed to process packet: {e}")

def run_server():
    logger.info("[Bank] Starting Classic Bluetooth (RFCOMM) Server...")
    
    # Check for key file
    if not os.path.exists(BANK_KEY_FILE):
        logger.warning("WARNING: Private key file not found! Decryption will fail.")

    try:
        # Create Bluetooth Socket (RFCOMM)
        server_sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        server_sock.bind((socket.BDADDR_ANY, RFCOMM_CHANNEL))
        server_sock.listen(1)

        logger.info(f"[Bank] Listening on RFCOMM Channel {RFCOMM_CHANNEL}...")
        logger.info("[Bank] Make sure this device is PAIRED with the Sender device.")

        while True:
            logger.info("Waiting for connection...")
            client_sock, address = server_sock.accept()
            logger.info(f"Accepted connection from {address}")

            try:
                full_data = b""
                while True:
                    chunk = client_sock.recv(4096)
                    if not chunk:
                        break
                    full_data += chunk
                
                if full_data:
                    logger.info(f"Received total {len(full_data)} bytes")
                    process_packet(full_data.decode('utf-8'))
            except Exception as e:
                logger.error(f"Error reading data: {e}")
            finally:
                client_sock.close()
                logger.info("Connection closed.")

    except AttributeError:
        logger.error("CRITICAL: Your Python version does not support socket.AF_BLUETOOTH.")
        logger.error("This usually means you are on Windows but using an old Python or a specific environment issue.")
    except OSError as e:
        if e.winerror == 10050:
            logger.error("CRITICAL: Bluetooth Adapter is OFF or NOT FOUND.")
            logger.error("--> Please TURN ON Bluetooth in Windows Settings.")
            logger.error("--> If it is on, try toggling it Off and On again.")
        else:
            logger.error(f"Server crashed: {e}")
    except Exception as e:
        logger.error(f"Server crashed: {e}")
    finally:
        if 'server_sock' in locals():
            server_sock.close()

if __name__ == "__main__":
    run_server()

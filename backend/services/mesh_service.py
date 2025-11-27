import socket
import json
import asyncio
from binascii import unhexlify
from bleak import BleakScanner
from Crypto.Cipher import AES as CryptoAES
from Crypto.Cipher import PKCS1_OAEP

from backend.crypto.bank_keys import load_bank_private_key
from backend.crypto.aes_utils import AES

# --- CONFIGURATION ---
RFCOMM_CHANNEL = 4
CACHED_BANK_MAC = None

# MANUAL OVERRIDE: If you know the MAC address of Device B, put it here.
# Example: "C8:F7:33:11:22:33"
# If this is set, scanning is skipped.
BANK_MAC_ADDRESS = "4C:5F:70:87:52:61"

# --- DECRYPTION HELPERS (For Local Simulation Fallback) ---
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

# --- BLUETOOTH CLIENT (RFCOMM) ---

async def scan_and_select_device():
    """
    Scans for BLE devices and asks user to select one.
    Returns the MAC address of the selected device.
    """
    print("[Mesh Service] Scanning for Bluetooth devices (5s)...")
    try:
        devices = await BleakScanner.discover(timeout=5.0)
    except Exception as e:
        print(f"[Mesh Service] Scanning failed: {e}")
        return None
    
    if not devices:
        print("[Mesh Service] No devices found.")
        return None

    # Filter out unnamed devices to reduce noise
    named_devices = [d for d in devices if d.name and d.name.strip()]
    
    if not named_devices:
        print("[Mesh Service] No named devices found.")
        return None

    print(f"\n[Mesh Service] Found {len(devices)} devices:")
    for i, dev in enumerate(devices):
        name = dev.name or "Unknown"
        print(f"  {i+1}. {name} ({dev.address})")

    # Auto-match "MeshBank"
    target = next((d for d in devices if d.name and "MeshBank" in d.name), None)
    
    if target:
        print(f"[Mesh Service] Auto-detected Bank Device: {target.name}")
        return target.address
    
    print("[Mesh Service] Could not auto-find device named 'MeshBank'.")
    print("[Mesh Service] Please rename the Bank Device to 'MeshBank' for auto-discovery.")
    return None

async def send_packet_via_rfcomm(packet: dict) -> bool:
    """
    Sends the encrypted packet via Classic Bluetooth (RFCOMM).
    """
    global CACHED_BANK_MAC
    
    # 0. Check Manual Override
    if BANK_MAC_ADDRESS and BANK_MAC_ADDRESS != "PUT_BANK_MAC_HERE":
        CACHED_BANK_MAC = BANK_MAC_ADDRESS

    # 1. Try to get MAC from Cache or Scan
    if not CACHED_BANK_MAC:
        CACHED_BANK_MAC = await scan_and_select_device()
        
    if not CACHED_BANK_MAC:
        print("[Mesh Service] ERROR: Could not find Bank Node.")
        print("TIP: Rename the other device to 'MeshBank' in Bluetooth Settings.")
        print("TIP: Or manually set BANK_MAC_ADDRESS in backend/services/mesh_service.py")
        return False

    print(f"[Mesh Service] Connecting to {CACHED_BANK_MAC} on Channel {RFCOMM_CHANNEL}...")
    
    try:
        # Create Bluetooth Socket
        # Note: socket.AF_BLUETOOTH is blocking. We wrap it.
        def _connect_and_send():
            sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            sock.connect((CACHED_BANK_MAC, RFCOMM_CHANNEL))
            data = json.dumps(packet).encode('utf-8')
            sock.send(data)
            sock.close()
            return True

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _connect_and_send)
        
        print("[Mesh Service] Packet sent successfully!")
        return True
    except Exception as e:
        print(f"[Mesh Service] RFCOMM Connection failed: {e}")
        # Clear cache in case MAC changed or device is wrong
        CACHED_BANK_MAC = None 
        return False

# --- MAIN ENTRY POINT ---

async def send_to_mesh(encrypted_packet: dict) -> bool:
    """
    Sends the encrypted packet via Bluetooth (RFCOMM).
    If Bluetooth fails, falls back to local simulation.
    """
    try:
        print("\n[Mesh Service] Initiating Bluetooth transmission...")
        
        success = await send_packet_via_rfcomm(encrypted_packet)
        
        if success:
            return True
            
        print("[Mesh Service] Bluetooth failed. Falling back to LOCAL SIMULATION (Single Device Mode)...")
        
        # --- LOCAL SIMULATION OF BANK NODE ---
        print("\n--- [DECRYPTION START (SIMULATED BANK)] ---")
        print(f"Received Encrypted Key: {encrypted_packet['encrypted_key'][:20]}...")
        
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

        from json import loads
        packet = loads(plaintext.decode("utf-8"))
        print("Dummy bank server received packet:", packet)
        return True
        # -------------------------------------

    except Exception as e:
        print(f"[Mesh Service] Transmission/Simulation failed: {e}")
        return False

import asyncio
import json
import logging
from typing import Any

from bless import (
    BlessServer,
    BlessGATTCharacteristic,
    GATTCharacteristicProperties,
    GATTAttributePermissions,
)

# Import decryption logic from backend
# Assuming this script is run from the project root
try:
    from backend.services.mesh_service import _rsa_decrypt_with_bank_private_key, _aes_decrypt_packet
except ImportError:
    print("Error: Could not import backend services. Make sure you are running from the project root.")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BankNode")

# UUIDs (Must match Sender and Relay)
MESH_SERVICE_UUID = "00000001-710e-4a5b-8d75-3e5b444bc3cf"
PACKET_CHARACTERISTIC_UUID = "00000002-710e-4a5b-8d75-3e5b444bc3cf"

def process_packet(packet: dict):
    """
    Decrypts and processes the received packet.
    """
    logger.info("\n--- [BANK NODE: PROCESSING PACKET] ---")
    try:
        logger.info(f"Received Encrypted Key: {packet['encrypted_key']}")
        
        # 1) Recover AES session key
        aes_key = _rsa_decrypt_with_bank_private_key(packet["encrypted_key"])
        logger.info(f"Decrypted AES Key: {aes_key.hex()}")

        # 2) Decrypt packet JSON
        plaintext = _aes_decrypt_packet(
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

def write_request_callback(
    characteristic: BlessGATTCharacteristic,
    value: Any,
    **kwargs
):
    """
    Callback when a device writes to the Packet Characteristic.
    """
    logger.info(f"[Bank] Received write request: {len(value)} bytes")
    try:
        packet = json.loads(value.decode('utf-8'))
        logger.info("[Bank] Packet received. Processing...")
        process_packet(packet)
    except Exception as e:
        logger.error(f"[Bank] Failed to parse packet: {e}")

async def run_bank_server(loop):
    logger.info("[Bank] Starting BLE Server...")
    
    # Initialize Server
    server = BlessServer(name="MeshBank", loop=loop)
    server.read_request_func = lambda x: x
    server.write_request_func = write_request_callback

    # Add Service
    await server.add_new_service(MESH_SERVICE_UUID)

    # Add Characteristic
    char_flags = (
        GATTCharacteristicProperties.write |
        GATTCharacteristicProperties.write_without_response
    )
    permissions = (
        GATTAttributePermissions.writeable
    )
    
    await server.add_new_characteristic(
        MESH_SERVICE_UUID,
        PACKET_CHARACTERISTIC_UUID,
        char_flags,
        None,
        permissions,
    )

    logger.info("[Bank] Advertising...")
    await server.start()
    
    # Keep running
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_bank_server(loop))
    except KeyboardInterrupt:
        pass

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
from bleak import BleakScanner, BleakClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RelayNode")

# UUIDs (Must match Sender and Bank)
MESH_SERVICE_UUID = "00000001-710e-4a5b-8d75-3e5b444bc3cf"
PACKET_CHARACTERISTIC_UUID = "00000002-710e-4a5b-8d75-3e5b444bc3cf"

# Global queue to store packets to be forwarded
packet_queue = asyncio.Queue()

def write_request_callback(
    characteristic: BlessGATTCharacteristic,
    value: Any,
    **kwargs
):
    """
    Callback when a device writes to the Packet Characteristic.
    """
    logger.info(f"[Relay] Received write request: {len(value)} bytes")
    try:
        # Decode just to ensure it's valid JSON, but we don't need to read the content
        # since it's encrypted.
        packet = json.loads(value.decode('utf-8'))
        logger.info("[Relay] Packet received successfully. Queuing for forward...")
        packet_queue.put_nowait(packet)
    except Exception as e:
        logger.error(f"[Relay] Failed to parse packet: {e}")

async def forward_packets():
    """
    Continuously monitors the queue and forwards packets to the next hop.
    """
    while True:
        packet = await packet_queue.get()
        logger.info("[Relay] Processing packet for forwarding...")
        
        # Scan for next hop (Bank or another Relay)
        # In a real mesh, we'd have routing logic. Here we just find ANY mesh node.
        # We should ideally avoid the node we just received from, but for simplicity:
        logger.info("[Relay] Scanning for next hop...")
        device = await BleakScanner.find_device_by_filter(
            lambda d, ad: MESH_SERVICE_UUID.lower() in [u.lower() for u in ad.service_uuids]
        )

        if not device:
            logger.warning("[Relay] No next hop found. Dropping packet (or retry logic needed).")
            packet_queue.task_done()
            continue

        logger.info(f"[Relay] Found next hop: {device.name} ({device.address})")
        
        try:
            async with BleakClient(device) as client:
                logger.info(f"[Relay] Connected to {device.address}")
                payload = json.dumps(packet).encode('utf-8')
                await client.write_gatt_char(PACKET_CHARACTERISTIC_UUID, payload, response=True)
                logger.info("[Relay] Packet forwarded successfully!")
        except Exception as e:
            logger.error(f"[Relay] Forwarding failed: {e}")
        
        packet_queue.task_done()

async def run_relay_server(loop):
    logger.info("[Relay] Starting BLE Server...")
    
    # Initialize Server
    server = BlessServer(name="MeshRelay", loop=loop)
    server.read_request_func = lambda x: x # No read needed
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

    logger.info("[Relay] Advertising...")
    await server.start()
    
    # Keep running
    while True:
        await asyncio.sleep(1)

async def main():
    loop = asyncio.get_running_loop()
    
    # Run Server and Forwarder concurrently
    await asyncio.gather(
        run_relay_server(loop),
        forward_packets()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

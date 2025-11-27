import asyncio
import json
from bleak import BleakScanner, BleakClient

# UUIDs for the Mesh Service
# These must match what the Relay and Bank nodes advertise.
MESH_SERVICE_UUID = "00000001-710e-4a5b-8d75-3e5b444bc3cf"
PACKET_CHARACTERISTIC_UUID = "00000002-710e-4a5b-8d75-3e5b444bc3cf"

async def send_packet_via_ble(packet: dict) -> bool:
    """
    Scans for a device advertising MESH_SERVICE_UUID, connects to it,
    and writes the packet as JSON bytes to PACKET_CHARACTERISTIC_UUID.
    """
    print(f"\n[BLE Sender] Scanning for Mesh Node ({MESH_SERVICE_UUID})...")
    
    device = await BleakScanner.find_device_by_filter(
        lambda d, ad: MESH_SERVICE_UUID.lower() in [u.lower() for u in ad.service_uuids]
    )

    if not device:
        print("[BLE Sender] No Mesh Node found.")
        return False

    print(f"[BLE Sender] Found Mesh Node: {device.name} ({device.address})")
    print("[BLE Sender] Connecting...")

    try:
        async with BleakClient(device) as client:
            print(f"[BLE Sender] Connected to {device.address}")
            
            # Convert packet to bytes
            payload = json.dumps(packet).encode('utf-8')
            
            # Write to characteristic
            # We might need to chunk if > MTU, but for now assuming small packets or Bleak handles it.
            # Bleak's write_gatt_char usually handles fragmentation if response=True? 
            # Actually standard BLE MTU is small (20-23 bytes), but modern is higher.
            # Bleak generally handles long writes if the device supports it.
            
            print(f"[BLE Sender] Sending {len(payload)} bytes...")
            await client.write_gatt_char(PACKET_CHARACTERISTIC_UUID, payload, response=True)
            
            print("[BLE Sender] Packet sent successfully!")
            return True
            
    except Exception as e:
        print(f"[BLE Sender] Error sending packet: {e}")
        return False

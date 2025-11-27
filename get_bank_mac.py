import asyncio
from bleak import BleakScanner

async def main():
    print("Scanning for 'MeshBank' (5 seconds)...")
    try:
        devices = await BleakScanner.discover(timeout=5.0)
        
        found = False
        for d in devices:
            name = d.name or "Unknown"
            if "MeshBank" in name:
                print(f"\nSUCCESS! Found Bank Node:")
                print(f"Name: {name}")
                print(f"Address: {d.address}")
                print("\n--> Please copy this Address into backend/services/mesh_service.py")
                found = True
                break
        
        if not found:
            print("\nDid not find 'MeshBank'.")
            print("Found these devices instead:")
            for d in devices:
                if d.name:
                    print(f" - {d.name} ({d.address})")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

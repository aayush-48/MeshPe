const SERVICE_UUID = '12345678-1234-1234-1234-123456789abc';
const CHARACTERISTIC_UUID = '87654321-4321-4321-4321-cba987654321';

export type EncryptedPayload = Record<string, any>;

export async function sendViaBLE(encryptedPayload: EncryptedPayload): Promise<boolean> {
  try {
    const nav = navigator as any;
    if (!nav.bluetooth) {
      throw new Error('Web Bluetooth API is not available in this browser');
    }

    const device = await nav.bluetooth.requestDevice({
      filters: [{ services: [SERVICE_UUID] }],
      optionalServices: [SERVICE_UUID]
    });

    if (!device.gatt) {
      throw new Error('GATT not available');
    }

    const server = await device.gatt.connect();
    const service = await server.getPrimaryService(SERVICE_UUID);
    const characteristic = await service.getCharacteristic(CHARACTERISTIC_UUID);

    const payloadString = JSON.stringify(encryptedPayload);
    const encoder = new TextEncoder();
    const payloadBytes = encoder.encode(payloadString);

    await characteristic.writeValue(payloadBytes);

    return true;
  } catch (error) {
    console.error('BLE Error:', error);
    throw error;
  }
}

export function checkBLESupport(): boolean {
  return 'bluetooth' in (navigator as any);
}

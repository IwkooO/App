import asyncio
import bleak

# Define your Arduino's service and characteristic UUIDs
service_uuid = "70fbdb96-eaff-4858-8d91-44b215525788"
characteristic_uuid = "70fbdb96-eaff-4858-8d91-44b215525788"

async def read_drunk_amount():
    # Scan for devices advertising the specified service UUID
    devices = await bleak.BleakScanner.discover()
    for device in devices:
        if service_uuid.lower() in device.metadata.get("uuids", []):
            device_address = device.address
            print(f"Found {device.name} at {device_address}")
            break  # Stop scanning once the device is found

    if 'device_address' not in locals():
        print("Device not found.")
        return

    async with bleak.BleakClient(device_address) as client:
        # Connect to the device
        await client.connect()
        print(f"Connected to {device.name} ({device.address})")

        # Discover services and characteristics
        await client.is_connected()
        await client.start_notify(characteristic_uuid)

        while True:
            drunk_amount_bytes = await client.read_gatt_char(characteristic_uuid)
            drunk_amount = int.from_bytes(drunk_amount_bytes, byteorder='little', signed=False)
            print(f"Received drunkAmount: {drunk_amount}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(read_drunk_amount())

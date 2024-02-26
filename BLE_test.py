import asyncio
from bleak import BleakScanner, BleakClient

async def list_devices():
    devices = await BleakScanner.discover()
    return devices

async def check_connectivity(client):
    while True:
        if client.is_connected:
            print("Device is connected.")
        else:
            print("Device got disconnected!")
            break
        await asyncio.sleep(5)  # Check every 5 seconds

async def main():
    devices = await list_devices()
    
    # List detected devices
    for i, device in enumerate(devices):
        print(f"{i}. {device.name} - {device.address}")

    # Get user input to select device
    index = int(input("Enter the index of the device you want to connect to: "))
    if index < 0 or index >= len(devices):
        print("Invalid index. Exiting...")
        return

    chosen_device = devices[index]
    async with BleakClient(chosen_device.address) as client:
        if not client.is_connected:
            print(f"Failed to connect to {chosen_device.name}")
            return
        print(f"Connected to {chosen_device.name}. Monitoring connectivity...")
        await check_connectivity(client)

if __name__ == "__main__":
    asyncio.run(main())

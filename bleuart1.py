import asyncio
from bleak import BleakClient, BleakScanner, BleakError
from datetime import datetime

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RXD_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TXD_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"

async def discover_devices():
    devices = await BleakScanner.discover()
    devices_with_names = [(device, device.rssi) for device in devices if device.name]
    for index, (device, rssi) in enumerate(devices_with_names):
        print(f"Index: {index}, Name: {device.name}, RSSI: {rssi}")
    return [device for device, _ in devices_with_names]


async def communicate_with_device(device):
    try:
        async with BleakClient(device.address) as client:
                            
            while True:
                # Get current date and time
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S \n')
                print(f"Current date and time: {current_time}")
                # Send current time to device
                await client.write_gatt_char(UART_TXD_UUID, current_time.encode())
                await asyncio.sleep(5)
                
                # Read data from device
                response = await client.read_gatt_char(UART_RXD_UUID)
                print(f"Received from device: {response.decode()}")
    except BleakError as e:
        print(f"Communication error: {e}") 


async def main():
    devices_with_names = await discover_devices()
    
    if not devices_with_names:
        print("No devices with names found. Exiting.")
        return

    try:
        choice = int(input("Enter the index of the device you want to connect to: "))
        if choice < 0 or choice >= len(devices_with_names):
            print("Invalid choice. Please choose a valid index.")
            return
        
        chosen_device = devices_with_names[choice]
        await communicate_with_device(chosen_device)
    except ValueError:
        print("Please enter a valid integer.")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

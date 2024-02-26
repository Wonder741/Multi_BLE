import asyncio
from bleak import BleakScanner, BleakClient
import datetime

async def scan_and_list_devices():
    devices = await BleakScanner.discover()
    return devices

async def send_datetime_to_device(address):
    async with BleakClient(address) as client:
        current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Assuming you have the characteristic UUID to which you want to send the datetime
        characteristic_uuid = "YOUR_CHARACTERISTIC_UUID_FOR_DATETIME"
        await client.write_gatt_char(characteristic_uuid, current_datetime.encode('utf-8'))

async def request_and_receive_file(address, file_path):
    async with BleakClient(address) as client:
        # Assuming you have the characteristic UUID from which you want to read the file data
        characteristic_uuid = "19B10000-E8F2-537E-4F6C-D104768A1214"
        file_data = await client.read_gatt_char(characteristic_uuid)
        with open(file_path, 'w') as file:
            file.write(file_data.decode('utf-8'))

async def check_connection(address):
    async with BleakClient(address) as client:
        return client.is_connected

def main():
    # Scan and list devices
    devices = asyncio.run(scan_and_list_devices())
    for idx, device in enumerate(devices):
        print(f"{idx + 1}. {device.name} - {device.address}")

    # Choose devices to connect
    selected_indices = input("Enter the indices of devices to connect to (e.g., '1' or '1,2'): ").split(',')
    selected_devices = [devices[int(idx) - 1] for idx in selected_indices]

    # Send datetime to selected devices
    for device in selected_devices:
        asyncio.run(send_datetime_to_device(device.address)) 
    
        # Check if devices are connected
    for device in selected_devices:
        is_connected = asyncio.run(check_connection(device.address))
        if not is_connected:
            print(f"Device {device.name} - {device.address} is not connected!")
            # Optionally, you can add logic to attempt a reconnection or skip operations for this device
            continue

    # Wait for another input
    input("Press Enter to send a file upload request...")

    # Request and receive files from selected devices
    for idx, device in enumerate(selected_devices):
        file_path = f"received_file_{idx + 1}.txt"
        asyncio.run(request_and_receive_file(device.address, file_path))
        print(f"File from {device.name} saved to {file_path}")

if __name__ == "__main__":
    main()

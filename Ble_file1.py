import asyncio
from bleak import BleakScanner, BleakClient

async def scan_and_list_devices():
    devices = await BleakScanner.discover()
    return devices

async def list_characteristics(address):
    async with BleakClient(address) as client:
        services = await client.get_services()
        characteristics = []
        for service in services:
            for char in service.characteristics:
                characteristics.append(char.uuid)
        return characteristics

async def read_from_characteristic(address, char_uuid):
    async with BleakClient(address) as client:
        return await client.read_gatt_char(char_uuid)

def main():
    # Scan and list devices
    devices = asyncio.run(scan_and_list_devices())
    for idx, device in enumerate(devices):
        print(f"{idx + 1}. {device.name} - {device.address}")

    # Choose a device
    selected_index = int(input("Enter the index of the device to connect to: ")) - 1
    selected_device = devices[selected_index]

    # Check connection
    client = BleakClient(selected_device.address)
    if not asyncio.run(client.connect()):
        print(f"Failed to connect to {selected_device.name} - {selected_device.address}")
        return
    else:
        print("Successfully connected!")

    # List available characteristic UUIDs
    char_uuids = asyncio.run(list_characteristics(selected_device.address))
    for idx, uuid in enumerate(char_uuids):
        print(f"{idx + 1}. UUID: {uuid}")

    # Choose a characteristic for file upload
    char_index = int(input("Enter the index of the characteristic for file upload: ")) - 1
    selected_char_uuid = char_uuids[char_index]

    # Read data and save locally
    file_data = asyncio.run(read_from_characteristic(selected_device.address, selected_char_uuid))
    with open("received_file.txt", 'w') as file:
        file.write(file_data.decode('utf-8'))
    print("File saved as received_file.txt")

if __name__ == "__main__":
    main()

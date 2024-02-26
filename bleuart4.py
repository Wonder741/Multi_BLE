import asyncio
import sys
from itertools import count, takewhile
from typing import Iterator

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

# UUIDs for the Nordic UART Service and its characteristics
UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

# Dictionary to store connected clients and their indices
connected_clients = {}  

# Function to slice data into chunks of a specified size
def sliced(data: bytes, n: int) -> Iterator[bytes]:
    return takewhile(len, (data[i: i + n] for i in count(0, n)))

# Main function for the program
async def main():
    # Function to match devices that advertise the UART service UUID
    def match_nus_uuid(device: BLEDevice, adv: AdvertisementData):
        return UART_SERVICE_UUID.lower() in adv.service_uuids

    # Discover all BLE devices and filter those that match the UART service UUID
    devices = await BleakScanner.discover()
    matching_devices = [device for device in devices if match_nus_uuid(device, device.metadata["advertisement_data"])]

    # If no matching devices are found, exit the program
    if not matching_devices:
        print("No matching devices found. Exiting.")
        sys.exit(1)

    # List the matching devices and prompt the user to select one
    print("Matching devices found:")
    for index, device in enumerate(matching_devices):
        print(f"{index}: {device.name}")

    device_index = int(input("Enter the index of the device to connect to: "))

    # Check if the entered index is valid
    if device_index < 0 or device_index >= len(matching_devices):
        print("Invalid index. Exiting.")
        sys.exit(1)

    # Select the device based on the user's input
    selected_device = matching_devices[device_index]

    # Function to handle device disconnection
    def handle_disconnect(client: BleakClient):
        print(f"Device {client.address} was disconnected.")
        del connected_clients[client.address]  # Remove the disconnected client from the list
        if not connected_clients:  # Check if there are no more connected clients
            print("All devices are disconnected, goodbye.")
            for task in asyncio.all_tasks():
                task.cancel()

    # Function to save received data to a text file
    def save_data_to_file(device_index, data):
        with open("received_data.txt", "a") as file:
            file.write(f"{device_index}: {data}\n")
    
    # Function to handle data received from the device
    def handle_rx(client: BleakClient, _: BleakGATTCharacteristic, data: bytearray):
        device_index = connected_clients.get(client.address, "Unknown")
        print(f"Received from device {device_index}:", data)
        save_data_to_file(device_index, data)

    # Connect to the selected device and set up notifications and data handling
    async with BleakClient(selected_device, disconnected_callback=handle_disconnect) as client:
        # Store the connected client with its index
        connected_clients[client.address] = device_index  
        for index, client in enumerate(connected_clients):
            await client.start_notify(UART_TX_CHAR_UUID, lambda _, data: handle_rx(index, _, data))

        print("Connected, start typing and press ENTER...")

    # Loop to read data from stdin and send it to all connected devices
    while True:
        data = await loop.run_in_executor(None, sys.stdin.buffer.readline)

        if not data:
            break

        for client in connected_clients:
            nus = client.services.get_service(UART_SERVICE_UUID)
            rx_char = nus.get_characteristic(UART_RX_CHAR_UUID)
            for s in sliced(data, rx_char.max_write_without_response_size):
                await client.write_gatt_char(rx_char, s, response=False)

        print("Sent:", data)

# Entry point of the program
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except asyncio.CancelledError:
        pass

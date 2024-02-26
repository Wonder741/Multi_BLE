import tkinter as tk
from tkinter import messagebox, scrolledtext
from bleak import BleakScanner, BleakClient
import asyncio
import threading

# UUIDs for UART service and characteristics
UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

class BLEGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BLE Device Manager")

        # Initialize variables
        self.devices = []
        self.connected_clients = {}
        self.messages = {}

        # Create GUI elements
        self.create_widgets()

        # Start the asyncio event loop
        self.loop = asyncio.get_event_loop()
        self.thread = threading.Thread(target=self.start_loop, daemon=True)
        self.thread.start()

    def create_widgets(self):
        # Buttons
        self.scan_button = tk.Button(self.root, text="Scan", command=self.scan)
        self.scan_button.grid(row=0, column=0, padx=5, pady=5)

        self.connect_button = tk.Button(self.root, text="Connect", command=self.connect)
        self.connect_button.grid(row=1, column=0, padx=5, pady=5)

        self.disconnect_button = tk.Button(self.root, text="Disconnect", command=self.disconnect)
        self.disconnect_button.grid(row=2, column=0, padx=5, pady=5)

        self.send_button = tk.Button(self.root, text="Send", command=self.send)
        self.send_button.grid(row=3, column=0, padx=5, pady=5)

        self.save_button = tk.Button(self.root, text="Save", command=self.save)
        self.save_button.grid(row=4, column=0, padx=5, pady=5)

        # Input boxes
        self.signal_filter_entry = tk.Entry(self.root)
        self.signal_filter_entry.grid(row=0, column=1, padx=5, pady=5)

        self.connect_entry = tk.Entry(self.root)
        self.connect_entry.grid(row=1, column=1, padx=5, pady=5)

        self.disconnect_entry = tk.Entry(self.root)
        self.disconnect_entry.grid(row=2, column=1, padx=5, pady=5)

        self.message_entry = tk.Entry(self.root)
        self.message_entry.grid(row=3, column=1, padx=5, pady=5)

        # Message boxes
        self.device_message_box = scrolledtext.ScrolledText(self.root, width=40, height=10)
        self.device_message_box.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        self.transmit_message_box = scrolledtext.ScrolledText(self.root, width=40, height=10)
        self.transmit_message_box.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

    def start_loop(self):
        self.loop.run_forever()

    async def scan(self):
        self.device_message_box.insert(tk.END, "Scanning for devices...\n")
        self.devices = await BleakScanner.discover()
        self.device_message_box.insert(tk.END, "Scan complete. Found devices:\n")
        for index, device in enumerate(self.devices):
            self.device_message_box.insert(tk.END, f"{index}: {device.name} ({device.rssi} dB)\n")

    async def connect(self):
        try:
            indices = [int(i) for i in self.connect_entry.get().split(',')]
            for index in indices:
                if index < 0 or index >= len(self.devices):
                    raise ValueError("Invalid device index")
                device = self.devices[index]
                self.device_message_box.insert(tk.END, f"Connecting to {device.name}...\n")
                client = BleakClient(device)
                await client.connect()
                self.connected_clients[index] = client
                self.device_message_box.insert(tk.END, f"Connected to {device.name}\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    async def disconnect(self):
        try:
            indices = [int(i) for i in self.disconnect_entry.get().split(',')]
            for index in indices:
                if index not in self.connected_clients:
                    raise ValueError("Invalid or not connected device index")
                client = self.connected_clients[index]
                await client.disconnect()
                del self.connected_clients[index]
                self.device_message_box.insert(tk.END, f"Disconnected from device {index}\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    async def send(self):
        message = self.message_entry.get().encode()
        for index, client in self.connected_clients.items():
            await client.write_gatt_char(UART_RX_CHAR_UUID, message)
            self.transmit_message_box.insert(tk.END, f"To {index}: {message.decode()}\n")

    def save(self):
        for index, messages in self.messages.items():
            with open(f"{index}.txt", "w") as file:
                for message in messages:
                    file.write(message + "\n")
            self.device_message_box.insert(tk.END, f"Saved messages from device {index} to {index}.txt\n")

    def on_closing(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.root.destroy()

def main():
    root = tk.Tk()
    app = BLEGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()

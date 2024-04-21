import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from PIL import Image
import matplotlib
import asyncio
import sys
import datetime
import csv
from itertools import islice
from queue import Queue
import threading

# Constants for BLE operations
UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

# Thread-safe queue for data exchange
data_queue = Queue()

# Visualization Thread function
def visualization_thread():
    # Load the background image
    bg_image = Image.open("background.png")
    bg_image_array = plt.imread("background.png")
    fig, ax = plt.subplots()
    ax.imshow(bg_image_array, extent=[0, bg_image.width, 0, bg_image.height])
    ax.set_xlim(0, bg_image.width)
    ax.set_ylim(0, bg_image.height)
    cmap = plt.get_cmap('jet')
    initial_color = cmap(0)
    coord_df = pd.read_csv("coordinates.csv")
    scatter = ax.scatter(coord_df['x'], coord_df['y'], color=[initial_color for _ in range(len(coord_df))], s=20)

    # Update function for the plot
    def update(frame):
        while not data_queue.empty():
            index, data = data_queue.get()
            print(f"Updating plot with data from device {index}")
            # Update logic for scatter plot colors based on new data

        return scatter,

    # Start animation
    ani = FuncAnimation(fig, update, interval=1000/60, blit=True)
    plt.show()

# Function to handle incoming BLE data
async def handle_rx(index, _, data):
    print(f"Received data from device {index}: {data}")
    data_queue.put((index, data))

# BLE Main function
async def main_ble():
    # BLE setup and connection code would go here
    # Dummy loop to simulate data reception
    while True:
        data = await asyncio.sleep(1, result="simulated data")
        handle_rx(0, None, data.encode())

# Start visualization thread
vis_thread = threading.Thread(target=visualization_thread)
vis_thread.start()

# Main event loop for BLE operations
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main_ble())
    except asyncio.CancelledError:
        pass

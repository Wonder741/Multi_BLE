import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from PIL import Image
import matplotlib

# Load the background image
bg_image = Image.open("background.png")
bg_image_array = plt.imread("background.png")

# Load the coordinates
coord_df = pd.read_csv("coordinates.csv")

# Set up the plot
fig, ax = plt.subplots()
ax.imshow(bg_image_array, extent=[0, bg_image.width, 0, bg_image.height])
ax.set_xlim(0, bg_image.width)
ax.set_ylim(0, bg_image.height)

# Create a colormap
cmap = plt.get_cmap('jet')

# Initialize colors to 0 for all points
initial_color = cmap(0)  # Get the color for value 0 on the colormap

# Scatter plot for all points initialized with the color for value 0
scatter = ax.scatter(coord_df['x'], coord_df['y'], color=[initial_color for _ in range(len(coord_df))], s=40)

# Function to update the points
def update(frame):
    data_L = pd.read_csv("dataL.csv")  # Load left device data
    data_R = pd.read_csv("dataR.csv")  # Load right device data
    # Convert data to float
    data_L = data_L.apply(pd.to_numeric, errors='coerce')
    data_R = data_R.apply(pd.to_numeric, errors='coerce')

    latest_data_L = data_L.iloc[-1]  # Get the latest row for left device
    latest_data_R = data_R.iloc[-1]  # Get the latest row for right device

    # Map the sensor values to colors for left device (IDs 1-16)
    colors_L = [cmap(latest_data_L.iloc[i] / 256) for i in range(9, 25)]
    # Map the sensor values to colors for right device (IDs 17-32)
    colors_R = [cmap(latest_data_R.iloc[i] / 256) for i in range(9, 25)]

    # Update the scatter plot colors
    for i, color in enumerate(colors_L):
        scatter._facecolors[i, :] = color  # IDs 1-16
    for i, color in enumerate(colors_R):
        scatter._facecolors[i + 16, :] = color  # IDs 17-32

    return scatter,

# Create the animation
ani = FuncAnimation(fig, update, interval=100, blit=True, cache_frame_data=False)

plt.show()

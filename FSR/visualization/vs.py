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
scatter = ax.scatter(coord_df['x'], coord_df['y'], color=[initial_color for _ in range(len(coord_df))], s=20)

# Function to update the points
def update(frame):
    data_df = pd.read_csv("data.csv")  # Reload the data
    latest_data = data_df.iloc[-1]  # Get the latest row
    device_type = latest_data[0]  # Determine which data row to use based on the device type

    # Determine which data indices to use based on device type
    if device_type == 'FSR_IMU_L':
        data_indices = range(9, 25)  # Columns 10-25 for left device data
        coord_subset = coord_df[coord_df['id'].between(1, 16)]
    if device_type == 'FSR_IMU_R':
        data_indices = range(9, 25)  # Columns 10-25 for right device data
        coord_subset = coord_df[coord_df['id'].between(17, 32)]

    # Map the sensor values to colors
    colors = [cmap(latest_data[i] / 1024) for i in data_indices]

    # Update the scatter plot colors
    for i, color in enumerate(colors):
        scatter._facecolors[coord_subset.index[i], :] = color

    return scatter,

# Create the animation
ani = FuncAnimation(fig, update, interval=1000/60, blit=True)

plt.show()

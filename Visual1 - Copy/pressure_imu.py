
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

# Set up the plot with specified subplot layout
fig = plt.figure(figsize=(10, 12))
ax1 = fig.add_subplot(2, 1, 1)  # Main animation plot, top half
ax2 = fig.add_subplot(2, 2, 3)  # Second subplot, bottom left
ax3 = fig.add_subplot(2, 2, 4)  # Third subplot, bottom right

# Main animation plot
ax1.imshow(bg_image_array, extent=[0, bg_image.width, 0, bg_image.height])
ax1.set_xlim(0, bg_image.width)
ax1.set_ylim(0, bg_image.height)

# Create a colormap
cmap = plt.get_cmap('jet')

# Initialize colors to 0 for all points
initial_color = cmap(0)  # Get the color for value 0 on the colormap

# Scatter plot for all points initialized with the color for value 0
scatter = ax1.scatter(coord_df['x'], coord_df['y'], color=[initial_color for _ in range(len(coord_df))], s=40)

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
    
    # Update data for the last 60 rows of columns 4-6 for dataL and dataR
    dataL = data_L.iloc[-30:, 3:6]
    dataR = data_R.iloc[-30:, 3:6]
    
    ax2.clear()
    ax3.clear()
    
    ax2.plot(dataL, label=['x', 'y', 'z'])
    ax3.plot(dataR, label=['x', 'y', 'z'])
    ax1.set_title('Pressure distribution')
    ax2.set_title('Acceleration left')
    ax3.set_title('Acceleration right')
    ax2.legend()
    ax3.legend()

    # Redrawing the canvas
    fig.canvas.draw()
    fig.canvas.flush_events()
    return scatter, ax2, ax3  # Include all updated artists

# Create the animation
ani = FuncAnimation(fig, update, interval=100, blit=True, cache_frame_data=False)

plt.show()

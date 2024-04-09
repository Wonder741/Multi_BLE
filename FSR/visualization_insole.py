import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from PIL import Image
import matplotlib

# Function to create a radial gradient
def create_radial_gradient(center_color, radius):
    y, x = np.ogrid[-radius:radius+1, -radius:radius+1]
    distance = np.sqrt(x**2 + y**2)

    max_distance = np.max(distance)
    normalized_distance = distance / max_distance

    gradient = np.ones((2*radius+1, 2*radius+1, 4))
    for i in range(3):
        gradient[:, :, i] = center_color[i] + (1 - center_color[i]) * normalized_distance

    gradient = np.clip(gradient, 0, 1)
    return gradient

# Load the background image
bg_image = Image.open("background.png")

# Load the coordinates
coord_df = pd.read_csv("coordinates1.csv").iloc[0:17]

# Set up the plot
fig, ax = plt.subplots()
ax.imshow(bg_image, extent=[0, 640, 0, 640])
ax.set_xlim(0, 640)
ax.set_ylim(0, 640)

# Create a colormap
cmap = matplotlib.colormaps['jet']

# Define the new radius
new_radius = 15

# Create gradient images for each area
gradient_images = []
for _, row in coord_df.iterrows():
    center_color = cmap(np.random.rand())[:3]
    gradient = create_radial_gradient(center_color, new_radius)
    gradient_image = ax.imshow(gradient, extent=[row['x']-new_radius, row['x']+new_radius, row['y']-new_radius, row['y']+new_radius], zorder=2)
    gradient_images.append(gradient_image)

# Update function for animation
def update(frame):
    data_df = pd.read_csv("data.csv")  # Reload the data
    latest_data = data_df.iloc[-1]  # Get the latest row
    for i, gradient_image in enumerate(gradient_images):
        value = latest_data[i - 16] / 400
        center_color = cmap(value)[:3]
        gradient = create_radial_gradient(center_color, new_radius)
        gradient_image.set_data(gradient)
    return gradient_images

# Create the animation
ani = FuncAnimation(fig, update, interval=20, blit=True, cache_frame_data=False)

plt.show()
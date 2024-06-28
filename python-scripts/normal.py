import rasterio
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

def read_raster_data(raster_path):
    with rasterio.open(raster_path) as raster:
        data = raster.read(1, masked=True)
        if raster.nodata is not None:
            data = data.filled(np.nan)
    return data

def flatten_data(data):
    return data.flatten()

# Replace 'traveltime.tif' with the path to your actual raster file
x_axis = flatten_data(read_raster_data('traveltime.tif'))

# Filter out NaN values
x_axis = x_axis[~np.isnan(x_axis)]

mean = np.mean(x_axis)
sd = np.std(x_axis)

# Plot histogram
plt.hist(x_axis, bins=50, density=True, alpha=0.6, color='g', range=(mean-3*sd, mean+3*sd))
xmin, xmax = plt.xlim()
plt.xlim(0,5)
plt.xlabel("Travel time in [h]")
plt.ylabel("Quantaty in percentage")
x = np.linspace(xmin, xmax, 100)


# Calculate and plot the 0.85 quantile
quantile_90 = np.quantile(x_axis, 0.90)
plt.axvline(x=quantile_90, color='r', linestyle='--', label='90%')
plt.legend()

plt.savefig("traveltimedistribution.png", dpi=300)  # Save the plot

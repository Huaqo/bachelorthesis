import rasterio
import numpy as np
from scipy.stats import pearsonr
import matplotlib.pyplot as plt

def read_raster_data(raster_path, target_width, target_height):
    with rasterio.open(raster_path) as raster:
        data = raster.read(1, masked=True)  # Reads the first band
        if data.shape != (target_height, target_width):
            data = data[:target_height, :target_width]
        if raster.nodata is not None:
            data = data.filled(np.nan)  # Fill masked values with NaN
    return data

def flatten_data(data):
    return data.flatten()

def calculate_correlation(data1, data2):
    mask = ~np.isnan(data1) & ~np.isnan(data2)
    
    filtered_data1 = data1[mask]
    filtered_data2 = data2[mask]
    
    correlation, _ = pearsonr(filtered_data1, filtered_data2)
    return correlation, filtered_data1, filtered_data2  # Return the filtered data for plotting

def plot_correlation(data1, data2, correlation, file_path):
    plt.scatter(data1, data2, alpha=0.5)
    plt.xlim(0,7)
    #plt.title(f'Correlation: {correlation:.2f}')
    plt.xlabel('Raster 1 Values')
    plt.ylabel('Raster 2 Values')
    plt.savefig(file_path, dpi=300)
    plt.close()
    

if __name__ == "__main__":
    raster_path1 = 'friction surface.tif'
    raster_path2 = 'ghsl.tif'
    save_path = 'plot.png'

    # Common dimensions
    target_width = 275  # Choose based on your requirements
    target_height = 254

    data1 = flatten_data(read_raster_data(raster_path1, target_width, target_height))
    data2 = flatten_data(read_raster_data(raster_path2, target_width, target_height))

    correlation, filtered_data1, filtered_data2 = calculate_correlation(data1, data2)
    plot_correlation(filtered_data1, filtered_data2, correlation, save_path)


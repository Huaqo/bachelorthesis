import rasterio
import numpy as np
from scipy.stats import pearsonr
from scipy.optimize import curve_fit
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
    return correlation, filtered_data1, filtered_data2

def exponential_func(x, a, b):
    return a * np.exp(-b * x)

def plot_max_values_scatter(data1, data2, file_path):
    # Group data by 0.01 increments
    bins = np.arange(0, np.nanmax(data1) + 0.001, 0.001)
    digitized = np.digitize(data1, bins)
    
    # Calculate the maximum of raster 2 values for each bin
    max_values_per_bin = []
    for i in range(1, len(bins)):
        filtered_data2 = data2[digitized == i]
        if filtered_data2.size > 0:  # Check if the array is not empty
            max_value = np.nanmax(filtered_data2)
        else:
            max_value = np.nan  # Set to NaN if no data is present in the bin
        max_values_per_bin.append(max_value)
    
    # Compute the indices of non-NaN values for max_values_per_bin
    non_nan_indices = ~np.isnan(max_values_per_bin)
    
    # Use these indices to filter both bins and max_values_per_bin
    max_values_per_bin = np.array(max_values_per_bin)[non_nan_indices]
    # Adjust the bin values to be the center of each bin for plotting
    bin_centers = bins[:-1] + 0.0005
    bin_centers = bin_centers[non_nan_indices]
    
    # Remove outliers based on a threshold (e.g., 3 standard deviations from the mean)
    threshold = np.nanmean(max_values_per_bin) + 3 * np.nanstd(max_values_per_bin)
    outliers_mask = max_values_per_bin <= threshold
    max_values_per_bin = max_values_per_bin[outliers_mask]
    bin_centers = bin_centers[outliers_mask]
    
    # Fit an exponential decrease to the scatter plot
    popt, pcov = curve_fit(exponential_func, bin_centers, max_values_per_bin)
    
    # Plot
    plt.scatter(bin_centers, max_values_per_bin, alpha=0.5, label='Data')
    plt.plot(bin_centers, exponential_func(bin_centers, *popt), 'r-', label='Exponential Fit')
    # Update labels to reflect the new bin size
    plt.xlabel('Population density in [%]')
    plt.ylabel('Friction surface in [min/km]')
    """plt.xlim(0,0.1)
    plt.ylim(0,0.1)"""
    plt.legend()
    plt.savefig(file_path, dpi=300)
    plt.close()


if __name__ == "__main__":
    raster_path2 = 'friction surface.tif'
    raster_path1 = 'ghsl.tif'
    save_path = 'plot_grouped_scatter_with_exponential_fit.png'

    # Common dimensions
    target_width = 275
    target_height = 254

    # Read and process the raster data
    data1 = flatten_data(read_raster_data(raster_path1, target_width, target_height))
    data2 = flatten_data(read_raster_data(raster_path2, target_width, target_height))

    # Calculate correlation
    correlation, filtered_data1, filtered_data2 = calculate_correlation(data1, data2)

    # Plot the maximum values of raster 2 for each group in raster 1
    plot_max_values_scatter(filtered_data1, filtered_data2, save_path)

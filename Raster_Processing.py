# Import required libraries
import rasterio
import geopandas as gpd
import numpy as np
from rasterio.mask import mask
import os
from sklearn.linear_model import LinearRegression
import pandas as pd
from scipy.stats import skew, kurtosis
import time

# Set machine-specific path
machine = "laptop"
if machine == "desktop":
    path = "E:/"
elif machine == "laptop":
    path = "C:/Users/clayz/"

start_time = time.time()  # Track script execution time

# Define seasons and coordinates for regions of interest (RoIs)
Seasons = ("Winter", "Spring", "Summer", "Autumn")
RoIs = ((13.2797, 55.7399), (18.2165, 57.2826), (13.0985, 59.0916),
        (21.7929, 65.6876), (18.0628, 59.3385), (16.6481, 66.3452),
        (22.7706, 68.2241), (16.1211, 63.1671), (20.1397, 63.8653),
        (14.8653, 57.4091))

# Timeframes matching each season
Seasons_TF = (('2022-12-01', '2023-02-28'),
              ('2023-03-01', '2023-05-31'),
              ('2023-06-01', '2023-08-31'),
              ('2023-09-01', '2023-11-30'))

# Predefined statistical metrics to calculate
Statistical_measures = {'Slope': None, 'Intercept': None, 'Average': None,
                        'Median': None, 'Skewness': None, 'Kurtosis': None,
                        'Standard Deviation': None}
keys = list(Statistical_measures.keys())

# Loop over locations
for count_location, point_roi in enumerate(RoIs):
    # Set path for output Excel files
    Location_data = f"{path}My Drive/.../Statistical_Data/Location_{count_location}"
    os.makedirs(Location_data, exist_ok=True)

    # Path to CORINE-based land cover shapefile
    class_shapefile_path = f"{path}My Drive/.../CORINNE_Location_{count_location}_Final.shp"
    class_shapefile = gpd.read_file(class_shapefile_path)

    # Loop over each season
    for count_season, TF in enumerate(Seasons_TF):
        # Initialize data container: (5 land classes, 4 bands, 7 stats)
        Data_array = np.zeros((5, 4, 7))
        
        # Output Excel path
        Excel_path = os.path.join(Location_data, f'Location_{count_location} {Seasons[count_season]}.xlsx')
        
        # Construct raster paths for L1C and L2A
        raster_L2A_path = f"{path}My Drive/.../L2A/Sentinel2_L2A_10m_Bands_{point_roi[0]}_{point_roi[1]}_{TF[0]}_{TF[1]}.tif"
        raster_L1C_path = f"{path}My Drive/.../L1C/Sentinel2_L1C_10m_Bands_{point_roi[0]}_{point_roi[1]}_{TF[0]}_{TF[1]}.tif"

        # Open both raster datasets
        with rasterio.open(raster_L2A_path) as src1, rasterio.open(raster_L1C_path) as src2:
            # Iterate over land cover classes (1 to 5)
            for n in range(1, 6):
                # Filter the class polygon
                polygon = class_shapefile[class_shapefile['Class'] == f'{n}']

                # Prepare to store results
                bands_set_L2A = {}
                bands_set_L1C = {}
                bands_regression_residual = {}

                # Loop through 4 spectral bands
                for i in range(1, 5):
                    # Read the bands
                    raster_L2A_band = src1.read(i)
                    raster_L1C_band = src2.read(i)

                    # Mask using current land class polygon
                    clipped_raster_L2A, _ = mask(src1, polygon.geometry, crop=True, indexes=i)
                    clipped_raster_L1C, _ = mask(src2, polygon.geometry, crop=True, indexes=i)

                    # Replace zeros with masked values
                    clipped_raster_L2A = np.where(clipped_raster_L2A == 0, 0, clipped_raster_L2A)
                    clipped_raster_L1C = np.where(clipped_raster_L1C == 0, 0, clipped_raster_L1C)

                    masked_L2A_Band = np.ma.masked_equal(clipped_raster_L2A, 0)
                    masked_L1C_Band = np.ma.masked_equal(clipped_raster_L1C, 0)

                    # Store original masked arrays
                    bands_set_L2A[f'Band_{i}'] = masked_L2A_Band
                    bands_set_L1C[f'Band_{i}'] = masked_L1C_Band

                    # Reshape arrays for regression
                    masked_L1C_Band_reshaped = masked_L1C_Band.reshape(-1, 1)
                    masked_L2A_Band_reshaped = masked_L2A_Band.reshape(-1, 1)

                    # Fit linear regression: L1C (X) vs L2A (Y)
                    model = LinearRegression()
                    model.fit(masked_L1C_Band_reshaped, masked_L2A_Band_reshaped)
                    predictions = model.predict(masked_L1C_Band_reshaped)

                    # Store slope and intercept
                    Statistical_measures[keys[0]] = model.coef_[0].item()
                    Statistical_measures[keys[1]] = model.intercept_.item()

                    # Compute residuals and statistics
                    residuals = np.abs(masked_L2A_Band_reshaped.astype(np.float64) - predictions)
                    bands_regression_residual[f'Band_{i}'] = residuals

                    Statistical_measures[keys[2]] = np.ma.mean(residuals)
                    Statistical_measures[keys[3]] = np.ma.median(residuals)
                    Statistical_measures[keys[4]] = skew(residuals).item()
                    Statistical_measures[keys[5]] = kurtosis(residuals).item()
                    Statistical_measures[keys[6]] = np.ma.std(residuals)

                    # Fill data array
                    for d, sm in enumerate(keys):
                        Data_array[n-1, i-1, d] = Statistical_measures[sm]

                    # Print progress
                    if i == 4:
                        print(f"Done from Location_{count_location} Class_{n} bands")
                        print("Time elapsed:", time.time() - start_time)

        # Save output to Excel (1 sheet per class)
        with pd.ExcelWriter(Excel_path) as writer:
            for m in range(Data_array.shape[0]):
                 df = pd.DataFrame(Data_array[m])
                 df.columns = keys
                 df['Band'] = [f'band {o}' for o in range(1, len(df) + 1)]
                 df.set_index('Band', inplace=True)
                 df.to_excel(writer, sheet_name=f'Class_{m+1}')
                
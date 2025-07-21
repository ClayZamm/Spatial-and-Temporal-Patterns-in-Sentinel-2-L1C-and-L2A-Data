import rasterio
import numpy as np
import os
from sklearn.linear_model import LinearRegression
import time

machine = "laptop"

if machine == "desktop":
    path = "E:/"
elif machine == "laptop":
    path = "C:/Users/clayz/"

start_time = time.time()

Seasons = ("Winter", "Spring", "Summer", "Autumn")

RoIs = ((13.2797, 55.7399),
        (18.2165, 57.2826),
        (13.0985, 59.0916),
        (21.7929, 65.6876),
        (18.0628, 59.3385),
        (16.6481, 66.3452),
        (22.7706, 68.2241),
        (16.1211, 63.1671),
        (20.1397, 63.8653),
        (14.8653, 57.4091))

Seasons_TF = (('2022-12-01', '2023-02-28'),
         ('2023-03-01', '2023-05-31'),
         ('2023-06-01', '2023-08-31'),
         ('2023-09-01', '2023-11-30'))

for count_location, point_roi in enumerate(RoIs, start=1):

    for count_season, TF in enumerate(Seasons_TF):
        save_path = f"C:/Users/clayz/Documents/RS_Project_Assignment_Data/Residuals/Location_{count_location}/{Seasons[count_season]}/"
        os.makedirs(save_path, exist_ok=True)

        raster_L2A_path = f"{path}My Drive/School stuff/Geomatics with Remote Sensing and GIS/1st Year/1st Semester/GE7088 Applied Remote Sensing and GIS for Landscape Analysis/Project/Data/Sentinel-2/Location_{count_location}/{Seasons[count_season]}/L2A/Sentinel2_L2A_10m_Bands_{point_roi[0]}_{point_roi[1]}_{TF[0]}_{TF[1]}.tif"
        raster_L1C_path = f"{path}My Drive/School stuff/Geomatics with Remote Sensing and GIS/1st Year/1st Semester/GE7088 Applied Remote Sensing and GIS for Landscape Analysis/Project/Data/Sentinel-2/Location_{count_location}/{Seasons[count_season]}/L1C/Sentinel2_L1C_10m_Bands_{point_roi[0]}_{point_roi[1]}_{TF[0]}_{TF[1]}.tif"
        
        with rasterio.open(raster_L2A_path) as src1, rasterio.open(raster_L1C_path) as src2:
            for i in range(1, 5):
                # Read the entire band without clipping
                raster_L2A_band = src1.read(i).astype(np.float64)
                raster_L1C_band = src2.read(i).astype(np.float64)
                # Directly work with the full bands
                valid_mask = raster_L1C_band != 0  # Create a mask for valid pixels
                masked_L1C_Band = raster_L1C_band[valid_mask]  # Filter invalid pixels
                masked_L2A_Band = raster_L2A_band[valid_mask]  # Filter invalid pixels

                # Reshape for regression
                masked_L1C_Band_reshaped = masked_L1C_Band.reshape(-1, 1)
                masked_L2A_Band_reshaped = masked_L2A_Band.reshape(-1, 1)

                model = LinearRegression()
                model.fit(masked_L1C_Band_reshaped, masked_L2A_Band_reshaped)
                predictions = model.predict(masked_L1C_Band_reshaped)

                residuals = np.abs(masked_L2A_Band_reshaped.astype(np.float64) - predictions)
                
                # Create a full residuals array and assign the values
                residuals_full = np.full(raster_L2A_band.shape, np.nan, dtype=np.float64)
                residuals /= 10000.0
                residuals[residuals > 1] = np.nan
                # Assign valid residuals (assumes the number of valid points is the same)
                residuals_full[valid_mask] = residuals.flatten()


                # Optional: Save residuals as raster files
                residuals_raster_path = os.path.join(save_path, f'Location_{count_location} {Seasons[count_season]} residuals_Band_{i}.tif')
                with rasterio.open(residuals_raster_path, 'w', driver='GTiff', height=residuals_full.shape[0], width=residuals_full.shape[1],
                                   count=1, dtype=residuals_full.dtype, crs=src1.crs, transform=src1.transform) as dst:
                    dst.write(residuals_full, 1)

                # Clean up variables if needed
                del predictions, residuals

                print(f"Done processing Band {i} for Location_{count_location} {Seasons[count_season]}")
                end_time = time.time()
                execution_time = end_time - start_time
                print(execution_time)


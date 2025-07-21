import rasterio
import geopandas as gpd
import numpy as np
from rasterio.mask import mask
import os
from sklearn.linear_model import LinearRegression
import pandas as pd
from scipy.stats import skew
from scipy.stats import kurtosis
import time

machine = "laptop"

if machine == "desktop":
    path = "E:/"
elif machine == "laptop":
    path = "C:/Users/clayz/"

start_time = time.time()

count_it = 0

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

Colours = [(0.165, 0.2, 0.75), (0.067, 0.74, 0.031), (0.882, 0.008, 0.008), (0.45, 0.033, 0.033)]

Statistical_measures = {'Slope': None, 'Intercept': None, 'Average': None, 'Median': None, 'Skewness': None, 'Kurtosis': None, 'Standard Deviation': None}
keys = list(Statistical_measures.keys())

def scale_ticks_x(axis, data):
    # Get current ticks
    ticks = axis.get_xticks()  # or get_yticks() for y-axis
    # Scale them to range from 0 to 1
    scaled_ticks = ticks / np.max(data)  # Adjust the maximum value based on your data
    # Set new ticks
    axis.set_xticks(ticks)
    axis.set_xticklabels(scaled_ticks)  # For x-axis, do the same for y-axis if needed
    
def scale_ticks_y(axis, data):
    # Get current ticks
    ticks = axis.get_yticks()  # or get_yticks() for y-axis
    # Scale them to range from 0 to 1
    scaled_ticks = ticks / np.max(data)  # Adjust the maximum value based on your data
    # Set new ticks
    axis.set_xticks(ticks)
    axis.set_xticklabels(scaled_ticks)  # For x-axis, do the same for y-axis if needed

for count_location, point_roi in enumerate(RoIs[3:], start=4):
    Location_data = f"{path}My Drive/School stuff/Geomatics with Remote Sensing and GIS/1st Year/1st Semester/GE7088 Applied Remote Sensing and GIS for Landscape Analysis/Project/Data/Statistical_Data/Location_{count_location}"
    os.makedirs(Location_data, exist_ok=True)
    class_shapefile_path = f"{path}My Drive/School stuff/Geomatics with Remote Sensing and GIS/1st Year/1st Semester/GE7088 Applied Remote Sensing and GIS for Landscape Analysis/Project/GIS/Outputs/CORINNE_Location_{count_location}_Final.shp"
    class_shapefile = gpd.read_file(class_shapefile_path)
    for count_season, TF in enumerate(Seasons_TF):
        Data_array = np.zeros((5, 4, 7))
        Excel_path = os.path.join(Location_data, f'Location_{count_location} {Seasons[count_season]}.xlsx')
        
        raster_L2A_path = f"{path}My Drive/School stuff/Geomatics with Remote Sensing and GIS/1st Year/1st Semester/GE7088 Applied Remote Sensing and GIS for Landscape Analysis/Project/Data/Sentinel-2/Location_{count_location}/{Seasons[count_season]}/L2A/Sentinel2_L2A_10m_Bands_{point_roi[0]}_{point_roi[1]}_{TF[0]}_{TF[1]}.tif"
        raster_L1C_path = f"{path}My Drive/School stuff/Geomatics with Remote Sensing and GIS/1st Year/1st Semester/GE7088 Applied Remote Sensing and GIS for Landscape Analysis/Project/Data/Sentinel-2/Location_{count_location}/{Seasons[count_season]}/L1C/Sentinel2_L1C_10m_Bands_{point_roi[0]}_{point_roi[1]}_{TF[0]}_{TF[1]}.tif"
        with rasterio.open(raster_L2A_path) as src1, rasterio.open(raster_L1C_path) as src2:
            for n in range(1, 6):
                polygon = class_shapefile[class_shapefile['Class'] == f'{n}']
            
                bands_set_L2A = {}
                bands_set_L1C = {}
                bands_regression_residual = {}
                # bands_slope = {}
                # bands_intercept = {}
                for i in range(1, 5):
                    raster_L2A_band = src1.read(i)
                    raster_L1C_band = src2.read(i)
                    
                    clipped_raster_L2A, out_transform1 = mask(src1, polygon.geometry, crop=True, indexes=i)
                    clipped_raster_L1C, out_transform2 = mask(src2, polygon.geometry, crop=True, indexes=i)
                    clipped_raster_L2A = np.where(clipped_raster_L2A == 0, 0, clipped_raster_L2A)
                    clipped_raster_L1C = np.where(clipped_raster_L1C == 0, 0, clipped_raster_L1C)
                    masked_L2A_Band = np.ma.masked_equal(clipped_raster_L2A, 0)
                    masked_L1C_Band = np.ma.masked_equal(clipped_raster_L1C, 0)

                    bands_set_L2A[f'Band_{i}'] = masked_L2A_Band
                    bands_set_L1C[f'Band_{i}'] = masked_L1C_Band
                    
                    masked_L1C_Band_reshaped = masked_L1C_Band.reshape(-1, 1)
                    masked_L2A_Band_reshaped = masked_L2A_Band.reshape(-1, 1)
                    masked_L1C_Band_1D = masked_L1C_Band.ravel()
                    masked_L2A_Band_1D = masked_L2A_Band.ravel()
                    # bands_slope[f'slope_{i}'], bands_intercept[f'intercept_{i}'] = np.polyfit(masked_L1C_Band_1D.astype(np.float32), masked_L2A_Band_1D.astype(np.float32), 1)
                    del masked_L1C_Band_1D
                    del masked_L2A_Band_1D
                    del masked_L1C_Band
                    del masked_L2A_Band
                    model = LinearRegression()
                    model.fit(masked_L1C_Band_reshaped, masked_L2A_Band_reshaped)
                    predictions = model.predict(masked_L1C_Band_reshaped)
                    del masked_L1C_Band_reshaped
                    Statistical_measures[keys[0]] = model.coef_[0].item()
                    Statistical_measures[keys[1]] = model.intercept_.item()
                    masked_L2A_Band_64 = masked_L2A_Band_reshaped.astype(np.float64)
                    del masked_L2A_Band_reshaped
                    residuals = np.abs(masked_L2A_Band_64 - predictions)
                    del predictions
                    del masked_L2A_Band_64
                    bands_regression_residual[f'Band_{i}'] = residuals
                    Statistical_measures[keys[2]] = np.ma.mean(residuals)
                    Statistical_measures[keys[3]] = np.ma.median(residuals)
                    Statistical_measures[keys[4]] = skew(residuals).item()
                    Statistical_measures[keys[5]] = kurtosis(residuals).item()
                    Statistical_measures[keys[6]] = np.ma.std(residuals)
                    del residuals
                    for d, sm in enumerate(keys):
                        Data_array[n-1, i-1, d] = Statistical_measures[sm]
                    if i == 4:
                        print(f"Done from Location_{count_location} Class_{n} bands")
                        end_time = time.time()
                        execution_time = end_time - start_time
                        print(execution_time)
                
        with pd.ExcelWriter(Excel_path) as writer:
            for m in range(Data_array.shape[0]):
                 df = pd.DataFrame(Data_array[m])
                 df.columns = keys
                 df['Band'] = [f'band {o}' for o in range(1, len(df) + 1)]
                 df.set_index('Band', inplace=True)
                 df.to_excel(writer, sheet_name=f'Class_{m+1}')
                
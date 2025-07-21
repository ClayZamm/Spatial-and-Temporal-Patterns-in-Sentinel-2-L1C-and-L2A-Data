import rasterio
import geopandas as gpd
import numpy as np
from rasterio.mask import mask
from scipy.stats import pearsonr, spearmanr, ttest_rel, f_oneway, ks_2samp
from shapely.geometry import Polygon
import matplotlib.pyplot as plt


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

Resolutions = ("10m", "20m", "60m")

def create_nodata_shapefile(nodata_mask, transform, output_shp):
    shapes = list(rasterio.features.shapes(nodata_mask.astype(np.uint8), transform=transform))
    geoms = [Polygon(shape[0]['coordinates'][0]) for shape in shapes if shape[1] == 0]
    gdf = gpd.GeoDataFrame(geometry=geoms)
    gdf.to_file(output_shp)

for count_location, point_roi in enumerate(RoIs, start=1):
    class_shapefile_path = f"C:/Users/clayz/My Drive/School stuff/Geomatics with Remote Sensing and GIS/1st Year/1st Semester/GE7088 Applied Remote Sensing and GIS for Landscape Analysis/Project/GIS/Outputs/CORINNE_Location_{count_location}_Final.shp"
    class_shapefile = gpd.read_file(class_shapefile_path)
    for n in range(1, 6):
        polygon = class_shapefile[class_shapefile['Class'] == f'{n}']
        for count_season, TF in enumerate(Seasons_TF):
            for res in Resolutions:
                raster_L2A_path = f"C:/Users/clayz/Documents/RS_Project_Assignment_Data/Sentinel-2/Location_{count_location}/{Seasons[count_season]}/L2A/Sentinel2_L2A_{res}_Bands_{point_roi[0]}_{point_roi[1]}_{TF[0]}_{TF[1]}.tif"
                raster_L1C_path = f"C:/Users/clayz/Documents/RS_Project_Assignment_Data/Sentinel-2/Location_{count_location}/{Seasons[count_season]}/L1C/Sentinel2_L1C_{res}_Bands_{point_roi[0]}_{point_roi[1]}_{TF[0]}_{TF[1]}.tif"
                with rasterio.open(raster_L2A_path) as src1, rasterio.open(raster_L1C_path) as src2:
                    
                    num_bands = src2.count
                    for i in range(1, num_bands+1):
                        raster_L2A_band = src1.read(i)
                        raster_L1C_band = src2.read(i)
                        
                        clipped_raster_L2A, out_transform1 = mask(raster_L2A_band, polygon.geometry, crop=True)
                        clipped_raster_L1C, out_transform2 = mask(raster_L1C_band, polygon.geometry, crop=True)
                        
                        nodata_L2A = src1.nodata
                        nodata_L1C = src2.nodata
                        mask_raster_L2A = clipped_raster_L2A != nodata_L2A
                        mask_raster_L1C = clipped_raster_L1C != nodata_L1C
                        valid_data_L2A = np.where(mask_raster_L2A, clipped_raster_L2A, np.nan)
                        valid_data_L1C = np.where(mask_raster_L1C, clipped_raster_L1C, np.nan)
                        combined_nodata_mask = mask_raster_L2A | mask_raster_L1C
                        
                        create_nodata_shapefile(~combined_nodata_mask, src1.transform, f'C:/Users/clayz/Documents/RS_Project_Assignment_Data/Sentinel-2/Location_{count_location}/{Seasons[count_season]}/Extent/Sentinel2_Location_{count_location}_{Seasons[count_season]}_nodata_extent.shp')
                        
                        
                        valid_mask = np.isfinite(clipped_valid_raster_L2A) & np.isfinite(clipped_valid_raster_L1C)
                        
                        pearson_corr, pearson_p = pearsonr(clipped_valid_raster_L2A, clipped_valid_raster_L1C)
                        
                        print(f"Slope: {slope}, Intercept: {intercept}, R-squared: {r_value**2}, P-value: {p_value}")
                        

meta = src1.meta.copy()

meta.update(dtype=rasterio.uint16,  # Set appropriate data type for the array
                count=1)

with rasterio.open("C:/Users/clayz/Documents/RS_Project_Assignment_Data/Sentinel-2/Experiment.tif", 'w', **meta) as dest:
        dest.write(valid_data_L2A.astype(rasterio.uint16), 1,1)

plt.figure(figsize=(10, 6))
plt.imshow(clipped_valid_raster_L2A, cmap='viridis', interpolation='nearest')
plt.colorbar(label='Float Values')  # Add a colorbar for reference
plt.title('Visualized Float Array as Map')
plt.xlabel('X-axis (Pixels)')
plt.ylabel('Y-axis (Pixels)')
plt.show()
                        
                        
                        
            
        
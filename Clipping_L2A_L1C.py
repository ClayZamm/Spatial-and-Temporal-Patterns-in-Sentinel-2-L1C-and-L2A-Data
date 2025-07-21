import rasterio
import geopandas as gpd
from shapely.geometry import box
from rasterio.mask import mask
import os
import numpy as np

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

def create_extent_shapefile(raster_path, output_shapefile):
    with rasterio.open(raster_path) as src:
        bounds = src.bounds
        # Create a GeoDataFrame with a rectangle that represents the raster's bounds
        gdf = gpd.GeoDataFrame({
            'geometry': [box(bounds.left, bounds.bottom, bounds.right, bounds.top)]
        }, crs=src.crs)
        gdf.to_file(output_shapefile)
        
def clip_raster_with_shapefile(raster_path, shapefile_path, output_path):
    with rasterio.open(raster_path) as src:
        # Read the shapefile
        shapes = gpd.read_file(shapefile_path)
        # Clip the raster using the shapefile
        out_image, out_transform = mask(src, shapes.geometry, crop=True)
        
        # Update the metadata
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })

        # Write the clipped raster to disk
        with rasterio.open(output_path, "w", **out_meta) as dest:
            dest.write(out_image)
            
def check_same_extent(shapefile1, shapefile2):
    # Load shapefiles
    gdf1 = gpd.read_file(shapefile1)
    gdf2 = gpd.read_file(shapefile2)
    
    # Get the bounds (left, bottom, right, top) for each shapefile
    bounds1 = gdf1.total_bounds  # returns [minx, miny, maxx, maxy]
    bounds2 = gdf2.total_bounds  # same format
    
    # Return True if bounding boxes are the same, False otherwise
    return np.array_equal(bounds1, bounds2)

Same_extent_list =[]

for count_location, point_roi in enumerate(RoIs, start=1):
    for count_season, TF in enumerate(Seasons_TF):
        for res in Resolutions:
            raster_L2A_path = f"C:/Users/clayz/Documents/RS_Project_Assignment_Data/Sentinel-2/Location_{count_location}/{Seasons[count_season]}/L2A/Sentinel2_L2A_{res}_Bands_{point_roi[0]}_{point_roi[1]}_{TF[0]}_{TF[1]}.tif"
            raster_L1C_path = f"C:/Users/clayz/Documents/RS_Project_Assignment_Data/Sentinel-2/Location_{count_location}/{Seasons[count_season]}/L1C/Sentinel2_L1C_{res}_Bands_{point_roi[0]}_{point_roi[1]}_{TF[0]}_{TF[1]}.tif"
            raster_L2A_path_clipped = f"C:/Users/clayz/Documents/RS_Project_Assignment_Data/Sentinel-2/Location_{count_location}/{Seasons[count_season]}/L2A/Sentinel2_L2A_{res}_Bands_{point_roi[0]}_{point_roi[1]}_{TF[0]}_{TF[1]}_clipped.tif"
            raster_L1C_path_clipped = f"C:/Users/clayz/Documents/RS_Project_Assignment_Data/Sentinel-2/Location_{count_location}/{Seasons[count_season]}/L1C/Sentinel2_L1C_{res}_Bands_{point_roi[0]}_{point_roi[1]}_{TF[0]}_{TF[1]}_clipped.tif"
            L2A_Temp_file_path = "C:/Users/clayz/Documents/RS_Project_Assignment_Data/Temp/L2A_Extent.shp"
            L1C_Temp_file_path = "C:/Users/clayz/Documents/RS_Project_Assignment_Data/Temp/L1C_Extent.shp"
            Extent_path = f"C:/Users/clayz/Documents/RS_Project_Assignment_Data/Sentinel-2/Location_{count_location}/{Seasons[count_season]}/Extent/Sentinel2_Location_{count_location}_{Seasons[count_season]}_extent.shp"
            os.makedirs(f"C:/Users/clayz/Documents/RS_Project_Assignment_Data/Sentinel-2/Location_{count_location}/{Seasons[count_season]}/Extent", exist_ok=True)
            
            create_extent_shapefile(raster_L2A_path, L2A_Temp_file_path)
            create_extent_shapefile(raster_L1C_path, L1C_Temp_file_path)
            
            extents_are_same = check_same_extent(L2A_Temp_file_path, L1C_Temp_file_path)
            
            if not extents_are_same:
                
                clip_raster_with_shapefile(raster_L2A_path, L1C_Temp_file_path, raster_L2A_path_clipped)
                clip_raster_with_shapefile(raster_L1C_path, L2A_Temp_file_path, raster_L1C_path_clipped)
                print(f"Location_{count_location} for {Seasons[count_season]} at {res} clipped")
                create_extent_shapefile(raster_L2A_path_clipped, Extent_path)
                os.remove(raster_L2A_path)
                os.remove(raster_L1C_path)
                
            else:
                print(f"Location_{count_location} for {Seasons[count_season]} at {res} are the same, thus skipping")
                create_extent_shapefile(raster_L2A_path, Extent_path)
                Same_extent_list.append(f"Location_{count_location}_{Seasons[count_season]}_{res}")
                
            
            

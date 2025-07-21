import rasterio
import numpy as np
import os
from rasterio.mask import mask

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


def clip_raster_to_match(src1, src2):
    """Clips src1 and src2 to their common overlapping area."""
    # Get bounding boxes
    bounds1 = src1.bounds
    bounds2 = src2.bounds

    # Get the intersection of both bounding boxes
    left = max(bounds1.left, bounds2.left)
    right = min(bounds1.right, bounds2.right)
    bottom = max(bounds1.bottom, bounds2.bottom)
    top = min(bounds1.top, bounds2.top)

    # Create a bounding box geometry for the intersection
    bbox = [{
        'type': 'Polygon',
        'coordinates': [[
            [left, top],
            [right, top],
            [right, bottom],
            [left, bottom],
            [left, top]
        ]]
    }]
    
    # Clip both rasters using the intersection
    clipped_src1, transform_src1 = mask(src1, bbox, crop=True)
    clipped_src2, transform_src2 = mask(src2, bbox, crop=True)
    
    return clipped_src1, clipped_src2, transform_src1

def process_clipped_rasters(clipped_src1, clipped_src2):
    """Processes the clipped rasters, for example by calculating the absolute difference."""
    # Ensure both clipped rasters have the same shape and bands
    min_bands = min(clipped_src1.shape[0], clipped_src2.shape[0])
    
    # Initialize list for processed bands
    processed_bands = []
    
    # Loop through the bands and calculate absolute difference
    for band in range(min_bands):
        difference_band = np.abs(clipped_src1[band] - clipped_src2[band])
        processed_bands.append(difference_band)
    
    # Stack processed bands back into a 3D array
    return np.stack(processed_bands)

for count_location, point_roi in enumerate(RoIs, start=1):
    for count_season, TF in enumerate(Seasons_TF):
        for res in Resolutions:
            raster_L2A_path = f"C:/Users/clayz/Documents/RS_Project_Assignment_Data/Sentinel-2/Location_{count_location}/{Seasons[count_season]}/L2A/Sentinel2_L2A_{res}_Bands_{point_roi[0]}_{point_roi[1]}_{TF[0]}_{TF[1]}.tif"
            raster_L1C_path = f"C:/Users/clayz/Documents/RS_Project_Assignment_Data/Sentinel-2/Location_{count_location}/{Seasons[count_season]}/L1C/Sentinel2_L1C_{res}_Bands_{point_roi[0]}_{point_roi[1]}_{TF[0]}_{TF[1]}.tif"
            output_path = f"C:/Users/clayz/Documents/RS_Project_Assignment_Data/Sentinel-2/Location_{count_location}/{Seasons[count_season]}/Difference/Sentinel2_Difference_{res}_Bands_{point_roi[0]}_{point_roi[1]}_{TF[0]}_{TF[1]}.tif"
            os.makedirs(f"C:/Users/clayz/Documents/RS_Project_Assignment_Data/Sentinel-2/Location_{count_location}/{Seasons[count_season]}/Difference", exist_ok=True)

            with rasterio.open(raster_L2A_path) as src1, rasterio.open(raster_L1C_path) as src2:
                    
                clipped_src1, clipped_src2, transform = clip_raster_to_match(src1, src2)
                # Get the number of bands in each raster
                bands_raster_L2A = src1.count
                bands_raster_L1C = src2.count
            
                # Determine the minimum number of bands to compare
                min_bands = min(bands_raster_L2A, bands_raster_L1C)
                
                # Prepare metadata for the output file, matching the first raster (with fewer bands)
                out_meta = src1.meta.copy()
                out_meta.update({"count": min_bands})  # Update the number of bands in metadata
                
                # Create an empty list to store the resulting bands
                result_bands = []
            
                # Loop through the minimum number of bands and subtract them
                for band in range(1, min_bands + 1):
                    raster_L2A_band = src1.read(band).astype('float32')
                    raster_L1C_band = src2.read(band).astype('float32')
            
                    # Example of band difference (you can modify this operation)
                    result_band = np.abs(raster_L2A_band - raster_L1C_band)
            
                    result_bands.append(result_band)
            
                # Convert the result_bands list to a 3D numpy array
                result_bands = np.stack(result_bands)
            
                # Write the result to a new output file
                with rasterio.open(output_path, 'w', **out_meta) as dst:
                    dst.write(result_bands)
                print(f'Location_{count_location} {Seasons[count_season]} for resolution {res} has been processed')
                    
                
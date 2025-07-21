import rasterio
import numpy as np
import os
from rasterio.mask import mask
from rasterio.enums import Resampling

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

bands_to_compare = ((1,2), (2,3), (3,4), (4,5))

for count_location, point_roi in enumerate(RoIs, start=1):
    for count_season, TF in enumerate(Seasons_TF):
        raster_L2A_path = f"C:/Users/clayz/Documents/RS_Project_Assignment_Data/Sentinel-2/Location_{count_location}/{Seasons[count_season]}/L2A/Sentinel2_L2A_10m_Bands_{point_roi[0]}_{point_roi[1]}_{TF[0]}_{TF[1]}.tif"
        raster_L8_path = f"C:/Users/clayz/Documents/RS_Project_Assignment_Data/Landsat-8/Location_{count_location}/{Seasons[count_season]}/Normalised/Landsat8_Processed_Location_{count_location}_{Seasons[count_season]}.tif"
        output_path = f"C:/Users/clayz/Documents/RS_Project_Assignment_Data/Differences_of_sat_types/Location_{count_location}/{Seasons[count_season]}/L8_S2L2A_difference.tif"
        os.makedirs(f"C:/Users/clayz/Documents/RS_Project_Assignment_Data/Differences_of_sat_types/Location_{count_location}/{Seasons[count_season]}", exist_ok=True)
        if os.path.exists(raster_L8_path):

            with rasterio.open(raster_L2A_path) as src1, rasterio.open(raster_L8_path) as src2:
                    
                clipped_src1, clipped_src2, transform = clip_raster_to_match(src1, src2)
                
                target_meta = src2.meta.copy()
                
                # Get the number of bands in each raster
                source_resolution = abs(src1.transform[0])  # Get the source pixel size (x-direction)
                target_resolution = abs(src2.transform[0])  # Get the target pixel size (x-direction)
                scale_factor = source_resolution / target_resolution
                
                
                # Create an empty list to store the resulting bands
                resampled_bands = []
                result_bands = []
            
                # Loop through the minimum number of bands and subtract them
                for current_band in bands_to_compare:
                    raster_L2A_band = clipped_src1.read(current_band[0], out_shape=(1, int(src1.height * scale_factor), int(src1.width * scale_factor)), resampling=Resampling.cubic).astype('float32')
                    raster_L8_band = clipped_src2.read(current_band[1]).astype('float32')
            
                    # Example of band difference (you can modify this operation)
                    result_band = np.abs(raster_L2A_band - raster_L8_band)
                    resampled_bands.append(result_band).append(result_band)
            
                # Convert the result_bands list to a 3D numpy array
                result_bands = np.stack(resampled_bands)
                
                target_meta.update({"count": result_bands.shape[0]})
            
                # Write the result to a new output file
                with rasterio.open(output_path, 'w', **target_meta) as dst:
                    dst.write(result_bands)
                print(f'Location_{count_location} {Seasons[count_season]} has been processed')
        else:
            print(f'Location_{count_location} {Seasons[count_season]} for L8 does not exist. Skipping...')
                    
import ee
import json
import os
import time

ee.Authenticate()
ee.Initialize()

RoIs = ((13.2797, 55.7399),
        (18.2165, 57.2826),
        (13.0985, 59.0916),
        (21.7929, 65.6876),
        (18.0628, 59.3385),
        (16.6481, 66.3452),
        (22.7706, 68.2241),
        (16.1211, 63.1671),
        (20.1397, 63.8653),
        (14.8653, 57.4091)  # Corrected last coordinates
        )

Seasons_TF = (('2022-12-01', '2023-02-28'),
              ('2023-03-01', '2023-05-31'),
              ('2023-06-01', '2023-08-31'),
              ('2023-09-01', '2023-11-30'),
              )

Season_name = ("Winter", "Spring", "Summer", "Autumn")

Copernicus = ('COPERNICUS/S2_HARMONIZED', 'COPERNICUS/S2_SR_HARMONIZED')


Missing_Sentinel_data = []

for count_location, point_roi in enumerate(RoIs, start=1):
    roi = ee.Geometry.Point(point_roi)
    for count_season, TF in enumerate(Seasons_TF):
        start_date = TF[0]
        end_date = TF[1]
                
        L2A_collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                      .filterBounds(roi)
                      .filterDate(start_date, end_date)
                      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
                      .sort('CLOUDY_PIXEL_PERCENTAGE'))
        best_L2A_image = L2A_collection.first()
        L2A_id = best_L2A_image.get('system:index')
        L2A_id_string = L2A_id.getInfo()  # Get the L2A image product ID
        
        L1C_collection = (ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
              .filterBounds(roi)
              .filter(ee.Filter.eq('system:index', L2A_id_string)))
        best_L1C_image = L1C_collection.first()
        
        if best_L2A_image and best_L1C_image:  # Make sure there is an image to export
            print(best_L2A_image.getInfo())
            
            image_footprint_L2A = best_L2A_image.geometry()
            image_footprint_L1C = best_L1C_image.geometry()
            
            # Define a folder structure
            folder_name_L2A = f"Location_{count_location}/{Season_name[count_season]}/L2A"
            folder_name_local_L2A = f"C:/Users/clayz/My Drive/School stuff/Geomatics with Remote Sensing and GIS/1st Year/1st Semester/GE7088 Applied Remote Sensing and GIS for Landscape Analysis/Project/Data/Location_{count_location}/{Season_name[count_season]}/L2A"
            folder_name_L1C = f"Location_{count_location}/{Season_name[count_season]}/L1C"
            folder_name_local_L1C = f"C:/Users/clayz/My Drive/School stuff/Geomatics with Remote Sensing and GIS/1st Year/1st Semester/GE7088 Applied Remote Sensing and GIS for Landscape Analysis/Project/Data/Location_{count_location}/{Season_name[count_season]}/L1C"
            
            # Create the directory structure if it doesn't exist
            os.makedirs(folder_name_local_L2A, exist_ok=True)
            os.makedirs(folder_name_local_L1C, exist_ok=True)# Creates all necessary directories

            # Export 10m bands
            task_10m_L2A = ee.batch.Export.image.toDrive(
                image=best_L2A_image.select(['B2', 'B3', 'B4', 'B8', 'AOT']),
                description=f"Sentinel2_L2A_10m_Bands_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}",
                region=image_footprint_L2A,
                scale=10,
                maxPixels=1e10,
                folder=folder_name_L2A  # Specify the folder name
            )

            # Export 20m bands
            task_20m_L2A = ee.batch.Export.image.toDrive(
                image=best_L2A_image.select(['B5', 'B6', 'B7', 'B8A', 'B11', 'B12']),
                description=f"Sentinel2_L2A_20m_Bands_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}",
                region=image_footprint_L2A,
                scale=20,
                maxPixels=1e10,
                folder=folder_name_L2A  # Specify the folder name
            )

            # Export 60m bands
            task_60m_L2A = ee.batch.Export.image.toDrive(
                image=best_L2A_image.select(['B1', 'B9']),
                description=f"Sentinel2_L2A_60m_Bands_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}",
                region=image_footprint_L2A,
                scale=60,
                maxPixels=1e10,
                folder=folder_name_L2A  # Specify the folder name
            )
            
            task_10m_L1C = ee.batch.Export.image.toDrive(
                image=best_L1C_image.select(['B2', 'B3', 'B4', 'B8']),
                description=f"Sentinel2_L1C_10m_Bands_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}",
                region=image_footprint_L1C,
                scale=10,
                maxPixels=1e10,
                folder=folder_name_L1C  # Specify the folder name
            )

            # Export 20m bands
            task_20m_L1C = ee.batch.Export.image.toDrive(
                image=best_L1C_image.select(['B5', 'B6', 'B7', 'B8A', 'B11', 'B12']),
                description=f"Sentinel2_L1C_20m_Bands_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}",
                region=image_footprint_L1C,
                scale=20,
                maxPixels=1e10,
                folder=folder_name_L1C  # Specify the folder name
            )

            # Export 60m bands
            task_60m_L1C = ee.batch.Export.image.toDrive(
                image=best_L1C_image.select(['B1', 'B9', 'B10']),
                description=f"Sentinel2_L1C_60m_Bands_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}",
                region=image_footprint_L1C,
                scale=60,
                maxPixels=1e10,
                folder=folder_name_L1C  # Specify the folder name
            )

            # Start the export tasks
            task_10m_L2A.start()
            task_20m_L2A.start()
            task_60m_L2A.start()
            task_10m_L1C.start()
            task_20m_L1C.start()
            task_60m_L1C.start()
            
            # Extract and save metadata
            metadata_L2A = best_L2A_image.getInfo()
            metadata_json_L2A = json.dumps(metadata_L2A, indent=4)
            metadata_filename_L2A = f"{folder_name_local_L2A}/metadata_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}.json"
            with open(metadata_filename_L2A, 'w') as f:
                f.write(metadata_json_L2A)
                
            metadata_L1C = best_L1C_image.getInfo()
            metadata_json_L1C = json.dumps(metadata_L1C, indent=4)    
            metadata_filename_L1C = f"{folder_name_local_L1C}/metadata_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}.json"
            with open(metadata_filename_L1C, 'w') as f:
                 f.write(metadata_json_L1C)
            
        else:
            print(f'Missing matching data for Location {count_location} suring {Season_name[count_season]}')
            Missing_Sentinel_data.append(f'Location {count_location} for {Season_name[count_season]} is missing for both')
            
# Import libraries
import ee
import json
import os
import time

# Authenticate and initialize Earth Engine
ee.Authenticate()
ee.Initialize()

# Define regions of interest (RoIs): coordinates for 10 locations in Sweden
RoIs = (
    (13.2797, 55.7399), (18.2165, 57.2826), (13.0985, 59.0916),
    (21.7929, 65.6876), (18.0628, 59.3385), (16.6481, 66.3452),
    (22.7706, 68.2241), (16.1211, 63.1671), (20.1397, 63.8653),
    (14.8653, 57.4091)
)

# Define timeframes representing each season
Seasons_TF = (
    ('2022-12-01', '2023-02-28'),
    ('2023-03-01', '2023-05-31'),
    ('2023-06-01', '2023-08-31'),
    ('2023-09-01', '2023-11-30'),
)
Season_name = ("Winter", "Spring", "Summer", "Autumn")

# Sentinel-2 image collections (Harmonized versions of L1C and L2A)
Copernicus = ('COPERNICUS/S2_HARMONIZED', 'COPERNICUS/S2_SR_HARMONIZED')

# Landsat-8 image collections (Collection 2 Tier 1)
Landsat8 = {
    "L1": 'LANDSAT/LC08/C02/T1_TOA',
    "L2": 'LANDSAT/LC08/C02/T1_L2',
}

L8_L2_BANDS_30M = ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', 'ST_B10']
L8_L2_BANDS_15M = ['SR_B8']
L8_L1_BANDS_30M = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B10', 'B11']
L8_L1_BANDS_15M = ['B8']

# Track locations with missing Sentinel data
Missing_Sentinel_data = []
Missing_Landsat_data = []

# === MAIN PROCESSING LOOP ===
for count_location, point_roi in enumerate(RoIs, start=1):
    roi = ee.Geometry.Point(point_roi)

    for count_season, TF in enumerate(Seasons_TF):
        start_date, end_date = TF

        # Filter Sentinel-2 L2A images (Surface Reflectance), cloud-free, within season and location
        L2A_collection = (
            ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
            .filterBounds(roi)
            .filterDate(start_date, end_date)
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
            .sort('CLOUDY_PIXEL_PERCENTAGE')
        )
        best_L2A_image = L2A_collection.first()  # Choose least cloudy

        # Get matching L1C image using the same 'system:index'
        L2A_id = best_L2A_image.get('system:index')
        L2A_id_string = L2A_id.getInfo()
        L1C_collection = (
            ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
            .filterBounds(roi)
            .filter(ee.Filter.eq('system:index', L2A_id_string))
        )
        best_L1C_image = L1C_collection.first()

        # Proceed only if both images exist
        if best_L2A_image and best_L1C_image:
            print(best_L2A_image.getInfo())

            # Get image footprints
            image_footprint_L2A = best_L2A_image.geometry()
            image_footprint_L1C = best_L1C_image.geometry()

            # Define folder structure for exports and metadata
            folder_name_L2A = f"Location_{count_location}/{Season_name[count_season]}/L2A"
            folder_name_L1C = f"Location_{count_location}/{Season_name[count_season]}/L1C"
            folder_name_local_L2A = f"C:/Users/clayz/.../Project/Data/{folder_name_L2A}"
            folder_name_local_L1C = f"C:/Users/clayz/.../Project/Data/{folder_name_L1C}"

            os.makedirs(folder_name_local_L2A, exist_ok=True)
            os.makedirs(folder_name_local_L1C, exist_ok=True)

            # === EXPORT L2A ===
            task_10m_L2A = ee.batch.Export.image.toDrive(
                image=best_L2A_image.select(['B2', 'B3', 'B4', 'B8', 'AOT']),
                description=f"Sentinel2_L2A_10m_Bands_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}",
                region=image_footprint_L2A,
                scale=10,
                maxPixels=1e10,
                folder=folder_name_L2A
            )

            task_20m_L2A = ee.batch.Export.image.toDrive(
                image=best_L2A_image.select(['B5', 'B6', 'B7', 'B8A', 'B11', 'B12']),
                description=f"Sentinel2_L2A_20m_Bands_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}",
                region=image_footprint_L2A,
                scale=20,
                maxPixels=1e10,
                folder=folder_name_L2A
            )

            task_60m_L2A = ee.batch.Export.image.toDrive(
                image=best_L2A_image.select(['B1', 'B9']),
                description=f"Sentinel2_L2A_60m_Bands_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}",
                region=image_footprint_L2A,
                scale=60,
                maxPixels=1e10,
                folder=folder_name_L2A
            )

            # === EXPORT L1C ===
            task_10m_L1C = ee.batch.Export.image.toDrive(
                image=best_L1C_image.select(['B2', 'B3', 'B4', 'B8']),
                description=f"Sentinel2_L1C_10m_Bands_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}",
                region=image_footprint_L1C,
                scale=10,
                maxPixels=1e10,
                folder=folder_name_L1C
            )

            task_20m_L1C = ee.batch.Export.image.toDrive(
                image=best_L1C_image.select(['B5', 'B6', 'B7', 'B8A', 'B11', 'B12']),
                description=f"Sentinel2_L1C_20m_Bands_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}",
                region=image_footprint_L1C,
                scale=20,
                maxPixels=1e10,
                folder=folder_name_L1C
            )

            task_60m_L1C = ee.batch.Export.image.toDrive(
                image=best_L1C_image.select(['B1', 'B9', 'B10']),
                description=f"Sentinel2_L1C_60m_Bands_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}",
                region=image_footprint_L1C,
                scale=60,
                maxPixels=1e10,
                folder=folder_name_L1C
            )

            # === Start all export tasks ===
            task_10m_L2A.start()
            task_20m_L2A.start()
            task_60m_L2A.start()
            task_10m_L1C.start()
            task_20m_L1C.start()
            task_60m_L1C.start()

            # === Save metadata locally ===
            metadata_L2A = best_L2A_image.getInfo()
            metadata_filename_L2A = f"{folder_name_local_L2A}/metadata_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}.json"
            with open(metadata_filename_L2A, 'w') as f:
                json.dump(metadata_L2A, f, indent=4)

            metadata_L1C = best_L1C_image.getInfo()
            metadata_filename_L1C = f"{folder_name_local_L1C}/metadata_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}.json"
            with open(metadata_filename_L1C, 'w') as f:
                json.dump(metadata_L1C, f, indent=4)

        else:
            # If no image found, log missing case
            print(f'Missing matching data for Location {count_location} during {Season_name[count_season]}')
            Missing_Sentinel_data.append(f'Location {count_location} for {Season_name[count_season]} is missing')

        # === LANDSAT-8 PROCESSING ===
        L8_L2_collection = (
            ee.ImageCollection(Landsat8["L2"])
            .filterBounds(roi)
            .filterDate(start_date, end_date)
            .filter(ee.Filter.lt('CLOUD_COVER', 30))
            .sort('CLOUD_COVER')
        )
        best_L8_L2_image = L8_L2_collection.first()

        if best_L8_L2_image:
            L8_L2_id = best_L8_L2_image.get('system:index')
            L8_L2_id_string = L8_L2_id.getInfo()
            L8_L1_collection = (
                ee.ImageCollection(Landsat8["L1"])
                .filterBounds(roi)
                .filter(ee.Filter.eq('system:index', L8_L2_id_string))
            )
            best_L8_L1_image = L8_L1_collection.first()
        else:
            best_L8_L1_image = None

        if best_L8_L2_image and best_L8_L1_image:
            print(best_L8_L2_image.getInfo())

            image_footprint_L8_L2 = best_L8_L2_image.geometry()
            image_footprint_L8_L1 = best_L8_L1_image.geometry()

            folder_name_L8_L2 = f"Location_{count_location}/{Season_name[count_season]}/Landsat8_L2"
            folder_name_L8_L1 = f"Location_{count_location}/{Season_name[count_season]}/Landsat8_L1"
            folder_name_local_L8_L2 = f"C:/Users/clayz/.../Project/Data/{folder_name_L8_L2}"
            folder_name_local_L8_L1 = f"C:/Users/clayz/.../Project/Data/{folder_name_L8_L1}"

            os.makedirs(folder_name_local_L8_L2, exist_ok=True)
            os.makedirs(folder_name_local_L8_L1, exist_ok=True)

            # === EXPORT LANDSAT-8 L2 ===
            task_30m_L8_L2 = ee.batch.Export.image.toDrive(
                image=best_L8_L2_image.select(L8_L2_BANDS_30M),
                description=f"Landsat8_L2_30m_Bands_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}",
                region=image_footprint_L8_L2,
                scale=30,
                maxPixels=1e10,
                folder=folder_name_L8_L2
            )

            task_15m_L8_L2 = ee.batch.Export.image.toDrive(
                image=best_L8_L2_image.select(L8_L2_BANDS_15M),
                description=f"Landsat8_L2_15m_Bands_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}",
                region=image_footprint_L8_L2,
                scale=15,
                maxPixels=1e10,
                folder=folder_name_L8_L2
            )

            # === EXPORT LANDSAT-8 L1 ===
            task_30m_L8_L1 = ee.batch.Export.image.toDrive(
                image=best_L8_L1_image.select(L8_L1_BANDS_30M),
                description=f"Landsat8_L1_30m_Bands_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}",
                region=image_footprint_L8_L1,
                scale=30,
                maxPixels=1e10,
                folder=folder_name_L8_L1
            )

            task_15m_L8_L1 = ee.batch.Export.image.toDrive(
                image=best_L8_L1_image.select(L8_L1_BANDS_15M),
                description=f"Landsat8_L1_15m_Bands_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}",
                region=image_footprint_L8_L1,
                scale=15,
                maxPixels=1e10,
                folder=folder_name_L8_L1
            )

            # === Start all export tasks ===
            task_30m_L8_L2.start()
            task_15m_L8_L2.start()
            task_30m_L8_L1.start()
            task_15m_L8_L1.start()

            # === Save metadata locally ===
            metadata_L8_L2 = best_L8_L2_image.getInfo()
            metadata_filename_L8_L2 = f"{folder_name_local_L8_L2}/metadata_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}.json"
            with open(metadata_filename_L8_L2, 'w') as f:
                json.dump(metadata_L8_L2, f, indent=4)

            metadata_L8_L1 = best_L8_L1_image.getInfo()
            metadata_filename_L8_L1 = f"{folder_name_local_L8_L1}/metadata_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}.json"
            with open(metadata_filename_L8_L1, 'w') as f:
                json.dump(metadata_L8_L1, f, indent=4)

        else:
            print(f'Missing Landsat-8 data for Location {count_location} during {Season_name[count_season]}')
            Missing_Landsat_data.append(f'Location {count_location} for {Season_name[count_season]} is missing')
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

# Landsat 8 image collections (Collection 2 Tier 1)
Landsat8 = ('LANDSAT/LC08/C02/T1_TOA', 'LANDSAT/LC08/C02/T1_L2')

# Track locations with missing data
Missing_Sentinel_data = []
Missing_Landsat_data = []


def export_tasks(tasks):
    """Start a list of Earth Engine export tasks."""
    for task in tasks:
        task.start()


def export_sentinel_pair(point_roi, count_location, count_season, start_date, end_date):
    """Export Sentinel-2 L1C/L2A image pair and save metadata."""
    roi = ee.Geometry.Point(point_roi)

    L2A_collection = (
        ee.ImageCollection(Copernicus[1])
        .filterBounds(roi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
        .sort('CLOUDY_PIXEL_PERCENTAGE')
    )
    best_L2A_image = L2A_collection.first()

    L2A_id = best_L2A_image.get('system:index')
    L2A_id_string = L2A_id.getInfo()
    L1C_collection = (
        ee.ImageCollection(Copernicus[0])
        .filterBounds(roi)
        .filter(ee.Filter.eq('system:index', L2A_id_string))
    )
    best_L1C_image = L1C_collection.first()

    if not (best_L2A_image and best_L1C_image):
        print(f'Missing matching Sentinel data for Location {count_location} during {Season_name[count_season]}')
        Missing_Sentinel_data.append(
            f'Location {count_location} for {Season_name[count_season]} is missing'
        )
        return

    image_footprint_L2A = best_L2A_image.geometry()
    image_footprint_L1C = best_L1C_image.geometry()

    folder_name_L2A = f"Location_{count_location}/{Season_name[count_season]}/L2A"
    folder_name_L1C = f"Location_{count_location}/{Season_name[count_season]}/L1C"
    folder_name_local_L2A = f"C:/Users/clayz/.../Project/Data/{folder_name_L2A}"
    folder_name_local_L1C = f"C:/Users/clayz/.../Project/Data/{folder_name_L1C}"

    os.makedirs(folder_name_local_L2A, exist_ok=True)
    os.makedirs(folder_name_local_L1C, exist_ok=True)

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

    export_tasks(
        [
            task_10m_L2A,
            task_20m_L2A,
            task_60m_L2A,
            task_10m_L1C,
            task_20m_L1C,
            task_60m_L1C,
        ]
    )

    metadata_L2A = best_L2A_image.getInfo()
    metadata_filename_L2A = (
        f"{folder_name_local_L2A}/metadata_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}.json"
    )
    with open(metadata_filename_L2A, 'w') as f:
        json.dump(metadata_L2A, f, indent=4)

    metadata_L1C = best_L1C_image.getInfo()
    metadata_filename_L1C = (
        f"{folder_name_local_L1C}/metadata_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}.json"
    )
    with open(metadata_filename_L1C, 'w') as f:
        json.dump(metadata_L1C, f, indent=4)


def export_landsat_pair(point_roi, count_location, count_season, start_date, end_date):
    """Export Landsat 8 L1 (TOA) / L2 (SR) image pair and save metadata."""
    roi = ee.Geometry.Point(point_roi)

    l8_sr_collection = (
        ee.ImageCollection(Landsat8[1])
        .filterBounds(roi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt('CLOUD_COVER', 30))
        .sort('CLOUD_COVER')
    )
    best_l8_sr = l8_sr_collection.first()

    l8_id = best_l8_sr.get('system:index')
    l8_id_string = l8_id.getInfo()
    l8_toa_collection = (
        ee.ImageCollection(Landsat8[0])
        .filterBounds(roi)
        .filter(ee.Filter.eq('system:index', l8_id_string))
    )
    best_l8_toa = l8_toa_collection.first()

    if not (best_l8_sr and best_l8_toa):
        print(f'Missing matching Landsat data for Location {count_location} during {Season_name[count_season]}')
        Missing_Landsat_data.append(
            f'Location {count_location} for {Season_name[count_season]} is missing'
        )
        return

    image_footprint_sr = best_l8_sr.geometry()
    image_footprint_toa = best_l8_toa.geometry()

    folder_name_l2 = f"Location_{count_location}/{Season_name[count_season]}/Landsat8_L2"
    folder_name_l1 = f"Location_{count_location}/{Season_name[count_season]}/Landsat8_L1"
    folder_name_local_l2 = f"C:/Users/clayz/.../Project/Data/{folder_name_l2}"
    folder_name_local_l1 = f"C:/Users/clayz/.../Project/Data/{folder_name_l1}"

    os.makedirs(folder_name_local_l2, exist_ok=True)
    os.makedirs(folder_name_local_l1, exist_ok=True)

    # Landsat 8 Surface Reflectance bands (30 m)
    l2_bands = ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']
    # Landsat 8 TOA bands (30 m)
    l1_bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7']

    l2_task = ee.batch.Export.image.toDrive(
        image=best_l8_sr.select(l2_bands),
        description=f"Landsat8_L2_30m_Bands_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}",
        region=image_footprint_sr,
        scale=30,
        maxPixels=1e10,
        folder=folder_name_l2,
    )

    l1_task = ee.batch.Export.image.toDrive(
        image=best_l8_toa.select(l1_bands),
        description=f"Landsat8_L1_30m_Bands_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}",
        region=image_footprint_toa,
        scale=30,
        maxPixels=1e10,
        folder=folder_name_l1,
    )

    export_tasks([l2_task, l1_task])

    metadata_l2 = best_l8_sr.getInfo()
    metadata_filename_l2 = (
        f"{folder_name_local_l2}/metadata_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}.json"
    )
    with open(metadata_filename_l2, 'w') as f:
        json.dump(metadata_l2, f, indent=4)

    metadata_l1 = best_l8_toa.getInfo()
    metadata_filename_l1 = (
        f"{folder_name_local_l1}/metadata_{point_roi[0]}_{point_roi[1]}_{start_date}_{end_date}.json"
    )
    with open(metadata_filename_l1, 'w') as f:
        json.dump(metadata_l1, f, indent=4)


# === MAIN PROCESSING LOOP ===
for count_location, point_roi in enumerate(RoIs, start=1):
    for count_season, TF in enumerate(Seasons_TF):
        start_date, end_date = TF
        export_sentinel_pair(point_roi, count_location, count_season, start_date, end_date)
        export_landsat_pair(point_roi, count_location, count_season, start_date, end_date)

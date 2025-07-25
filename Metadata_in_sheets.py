# Import necessary libraries
import json
import pandas as pd
import datetime
import numpy as np

# Define seasons and Sentinel-2 product levels
Seasons = ("Winter", "Spring", "Summer", "Autumn")
Sent_2_versions = ("L1C", "L2A")

# Define coordinates for 10 Regions of Interest (RoIs)
RoIs = (
    (13.2797, 55.7399), (18.2165, 57.2826), (13.0985, 59.0916),
    (21.7929, 65.6876), (18.0628, 59.3385), (16.6481, 66.3452),
    (22.7706, 68.2241), (16.1211, 63.1671), (20.1397, 63.8653),
    (14.8653, 57.4091)
)

# Time ranges defining each season
Seasons_TF = (
    ('2022-12-01', '2023-02-28'),
    ('2023-03-01', '2023-05-31'),
    ('2023-06-01', '2023-08-31'),
    ('2023-09-01', '2023-11-30')
)

# Output Excel file paths
new_excel_file_bands = r'C:\Users\clayz\My Drive\...Metadata_excel_bands.xlsx'
new_excel_file_total = r'C:\Users\clayz\My Drive\...Metadata_excel_total.xlsx'

# Column names to extract from metadata JSON
Columns_data_for_bands = [
    "MEAN_INCIDENCE_AZIMUTH_ANGLE",
    "MEAN_INCIDENCE_ZENITH_ANGLE",
    "SOLAR_IRRADIANCE"
]
Columns_data_for_total = [
    "CLOUDY_PIXEL_PERCENTAGE",
    "system:time_end",
    "MEAN_SOLAR_AZIMUTH_ANGLE",
    "MEAN_SOLAR_ZENITH_ANGLE"
]
Bands = ['B2', 'B3', 'B4', 'B8']

# === PART 1: Extract GENERAL metadata (not band-specific) ===

# Create a 3D array to store total metadata for all locations/seasons
array = np.zeros((1, 40, 4), dtype=object)  # 1 block, 40 entries, 4 features each
j = 0
loc_season = []  # Track location-season identifiers for indexing

# Loop through each location and season to populate array
for count_location, point_roi in enumerate(RoIs, start=1):
    for count_season, TF in enumerate(Seasons_TF):
        # Add location & season label
        loc_season.append(f'Location_{count_location} {Seasons[count_season]}')
        
        # Path to the corresponding metadata JSON
        metadata_path = f"C:/Users/clayz/.../Location_{count_location}/{Seasons[count_season]}/L2A/metadata_{point_roi[0]}_{point_roi[1]}_{TF[0]}_{TF[1]}.json"
        
        # Load and extract selected metadata
        with open(metadata_path, 'r') as file:
            data = json.load(file)
            for column_index, column_name in enumerate(Columns_data_for_total):
                value = data['properties'][f'{column_name}']
                
                # Convert timestamp to human-readable date
                if column_name == "system:time_end":
                    value = value / 1000  # Convert from ms to seconds
                    value = datetime.datetime.fromtimestamp(value).strftime("%Y-%m-%d")
                
                array[0, j, column_index] = value
        
        j += 1

# Save total metadata to Excel
with pd.ExcelWriter(new_excel_file_total) as writer:
    df_array = pd.DataFrame(array[0])
    df_array.columns = Columns_data_for_total
    df_array['location & Season'] = loc_season
    df_array.set_index('location & Season', inplace=True)
    df_array.to_excel(writer, sheet_name='total')

# === PART 2: Extract BAND-SPECIFIC metadata ===

# Create a 3D array for 4 bands × 40 entries × 3 features
array = np.zeros((4, 40, 3), dtype=object)
j = 0  # Reset index counter

# Loop through each location and season again
for count_location, point_roi in enumerate(RoIs, start=1):
    for count_season, TF in enumerate(Seasons_TF):
        # Path to metadata JSON
        metadata_path = f"C:/Users/clayz/.../Location_{count_location}/{Seasons[count_season]}/L2A/metadata_{point_roi[0]}_{point_roi[1]}_{TF[0]}_{TF[1]}.json"
        
        with open(metadata_path, 'r') as file:
            data = json.load(file)
            # Loop over bands (B2–B8) and extract relevant columns
            for num_band, band in enumerate(Bands):
                for column_index, column_name in enumerate(Columns_data_for_bands):
                    value = data['properties'][f'{column_name}_{band}']
                    array[num_band, j, column_index] = value
        j += 1

# Save band-specific metadata to Excel, one sheet per band
with pd.ExcelWriter(new_excel_file_bands) as writer:
    for m in range(array.shape[0]):
         df_array = pd.DataFrame(array[m])
         df_array.columns = Columns_data_for_bands
         df_array['location & Season'] = loc_season
         df_array.set_index('location & Season', inplace=True)
         df_array.to_excel(writer, sheet_name=f'Band_{m+1}')
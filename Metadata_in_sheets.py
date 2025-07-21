import json
import pandas as pd
import datetime
import numpy as np

Seasons = ("Winter", "Spring", "Summer", "Autumn")
Sent_2_versions = ("L1C", "L2A")

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

new_excel_file_bands = r'C:\Users\clayz\My Drive\School stuff\Geomatics with Remote Sensing and GIS\1st Year\1st Semester\GE7088 Applied Remote Sensing and GIS for Landscape Analysis\Project\Data\Metadata\Metadata_excel_bands.xlsx'
new_excel_file_total = r'C:\Users\clayz\My Drive\School stuff\Geomatics with Remote Sensing and GIS\1st Year\1st Semester\GE7088 Applied Remote Sensing and GIS for Landscape Analysis\Project\Data\Metadata\Metadata_excel_total.xlsx'
Columns_data_for_bands = ["MEAN_INCIDENCE_AZIMUTH_ANGLE", "MEAN_INCIDENCE_ZENITH_ANGLE", "SOLAR_IRRADIANCE"]
Columns_data_for_total = ["CLOUDY_PIXEL_PERCENTAGE", "system:time_end", "MEAN_SOLAR_AZIMUTH_ANGLE", 'MEAN_SOLAR_ZENITH_ANGLE']
Bands = ['B2', 'B3', 'B4', 'B8']



array = np.zeros((1, 40, 4))
array = array.astype(object)
j = 0

loc_season = []
for count_location, point_roi in enumerate(RoIs, start=1):
    for count_season, TF in enumerate(Seasons_TF):
        loc_season.append(f'Location_{count_location} {Seasons[count_season]}')
        metadata_path = f"C:/Users/clayz/My Drive/School stuff/Geomatics with Remote Sensing and GIS/1st Year/1st Semester/GE7088 Applied Remote Sensing and GIS for Landscape Analysis/Project/Data/Sentinel-2/Location_{count_location}/{Seasons[count_season]}/L2A/metadata_{point_roi[0]}_{point_roi[1]}_{TF[0]}_{TF[1]}.json"
        with open(metadata_path, 'r') as file:
            data = json.load(file)
            for column_index, column_name in enumerate(Columns_data_for_total): 
                data_to_add = data['properties'][f'{column_name}']
                if column_name == "system:time_end":
                    data_to_add = data_to_add / 1000
                    data_to_add = datetime.datetime.fromtimestamp(data_to_add)
                    data_to_add = data_to_add.strftime("%Y-%m-%d")
                    array[0, j, column_index] = data_to_add
                else:
                    array[0, j, column_index] = data_to_add
        j = j + 1
    
with pd.ExcelWriter(new_excel_file_total) as writer:
    df_array = pd.DataFrame(array[0])
    df_array.columns = Columns_data_for_total
    df_array['location & Season'] = loc_season
    df_array.set_index('location & Season', inplace=True)
    df_array.to_excel(writer, sheet_name='total')

array = np.zeros((4, 40, 3))
array = array.astype(object)
j = 0

for count_location, point_roi in enumerate(RoIs, start=1):
    for count_season, TF in enumerate(Seasons_TF):
        metadata_path = f"C:/Users/clayz/My Drive/School stuff/Geomatics with Remote Sensing and GIS/1st Year/1st Semester/GE7088 Applied Remote Sensing and GIS for Landscape Analysis/Project/Data/Sentinel-2/Location_{count_location}/{Seasons[count_season]}/L2A/metadata_{point_roi[0]}_{point_roi[1]}_{TF[0]}_{TF[1]}.json"
        with open(metadata_path, 'r') as file:
            data = json.load(file)
            for num_band, band in enumerate(Bands):
                for column_index, column_name in enumerate(Columns_data_for_bands): 
                    data_to_add = data['properties'][f'{column_name}_{band}']
                    array[num_band, j, column_index] = data_to_add
        j = j + 1

    
with pd.ExcelWriter(new_excel_file_bands) as writer:
    for m in range(array.shape[0]):
         df_array = pd.DataFrame(array[m])
         df_array.columns = Columns_data_for_bands
         df_array['location & Season'] = loc_season
         df_array.set_index('location & Season', inplace=True)
         df_array.to_excel(writer, sheet_name=f'Band_{m+1}')
                                         
                    
            

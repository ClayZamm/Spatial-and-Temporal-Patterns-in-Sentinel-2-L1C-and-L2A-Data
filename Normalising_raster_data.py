import rasterio
import os

Sat_types = ("Sentinel-2", "Landsat-8")
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

TS_TE = (('2022-12-01', '2023-02-28'),
         ('2023-03-01', '2023-05-31'),
         ('2023-06-01', '2023-08-31'),
         ('2023-09-01', '2023-11-30'))

Missing_Landsat8_data = []

for count_location, roi in enumerate(RoIs, start=1):
    for count_season, time_range in enumerate(TS_TE):
        try:
            input_file = f'C:/Users/clayz/Documents/RS_Project_Assignment_Data/Landsat-8/Location_{count_location}/{Seasons[count_season]}/Landsat8_Location_{count_location}_{Seasons[count_season]}.tif'
            output_file = f'C:/Users/clayz/Documents/RS_Project_Assignment_Data/Landsat-8/Location_{count_location}/{Seasons[count_season]}/Normalised/Landsat8_Processed_Location_{count_location}_{Seasons[count_season]}.tif'

            with rasterio.open(input_file) as src:
                profile = src.profile
                profile.update(dtype=rasterio.float32)  # Ensure the output has the correct data type

                os.makedirs(os.path.dirname(output_file), exist_ok=True)

                with rasterio.open(output_file, 'w', **profile) as dst:
                    scaling_factor = 10000.0 / 65535.0
                    for band in range(1, src.count + 1):
                        data = src.read(band)
                        data = data * scaling_factor # Normalize data
                        data = data.astype(rasterio.uint16)
                        dst.write(data, band)
                        print(f"Location_{count_location} during {Seasons[count_season]} band_{band} has been processed")
        except rasterio.errors.RasterioIOError:
            Missing_Landsat8_data.append(f"Location_{count_location}_{Seasons[count_season]}")
                
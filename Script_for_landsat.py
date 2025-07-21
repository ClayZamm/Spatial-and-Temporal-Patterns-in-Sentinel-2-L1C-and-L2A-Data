import json
import ee
import os

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

missing_data = []

for count_location, point_roi in enumerate(RoIs, start=1):
    for count_season, TF in enumerate(Seasons_TF):
      with open(f'C:/Users/clayz/Documents/RS_Project_Assignment_Data/Sentinel-2/Location_{count_location}/{Season_name[count_season]}/L2A/metadata_{point_roi[0]}_{point_roi[1]}_{TF[0]}_{TF[1]}.json', 'r') as file:
          sentinel_metadata = json.load(file)
          date = f"{sentinel_metadata['id'][28:32]}-{sentinel_metadata['id'][32:34]}-{sentinel_metadata['id'][34:36]}"
          
          sentinel_date = ee.Date(date)
          start_date = sentinel_date.advance(-3, 'day')
          end_date = sentinel_date.advance(3, 'day')
          
          Sentinel_polygon = ee.Geometry.Polygon(sentinel_metadata['properties']['system:footprint']['coordinates'])
          landsat_collection = (ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
                      .filterDate(start_date, end_date)
                      .filterBounds(Sentinel_polygon)
                      .filter(ee.Filter.lt('CLOUD_COVER', 40))  # Cloud cover threshold
                     )
          
          folder_name_L8 = f"Location_{count_location}/{Season_name[count_season]}/Landsat"
          folder_name_local_L8 = f"C:/Users/clayz/Documents/RS_Project_Assignment_Data/Landsat-8/Location_{count_location}/{Season_name[count_season]}"
          os.makedirs(folder_name_local_L8, exist_ok=True)
          
          def calculate_coverage(image):
              landsat_footprint = image.geometry()
              intersection = landsat_footprint.intersection(Sentinel_polygon, ee.ErrorMargin(1))
              coverage_ratio = intersection.area().divide(Sentinel_polygon.area())
              return image.set('coverage', coverage_ratio)
          
          landsat_with_coverage = landsat_collection.map(calculate_coverage)
          
          # Filter images to retain only those covering >= 30% of the Sentinel-2 area
          landsat_filtered = landsat_with_coverage.filter(ee.Filter.gte('coverage', 0.3))
          
          # Get the best image (e.g., the one with the least cloud cover)
          best_image = landsat_filtered.sort('CLOUD_COVER').first()
          
          # Export the best image if one is found
          if best_image:
              task = ee.batch.Export.image.toDrive(
                  image=best_image.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']),
                  description=f'Landsat8_Location_{count_location}_{Season_name[count_season]}',
                  folder=folder_name_L8,
                  region=Sentinel_polygon,
                  scale=30,  # Landsat-8 spatial resolution
                  maxPixels=1e8
                 )
              task.start()
              
             
              
              metadata_L8 = best_image.getInfo()
              metadata_json_L8 = json.dumps(metadata_L8, indent=4)
              metadata_filename_L8 = f"{folder_name_local_L8}/L8_metadata_{point_roi[0]}_{point_roi[1]}_{Season_name[count_season]}.json"
              with open(metadata_filename_L8, 'w') as f:
                  f.write(metadata_json_L8)
          else:
              missing_data.append(f'Landsat Location {count_location} for {Season_name[count_season]} is missing')
              
print(missing_data)

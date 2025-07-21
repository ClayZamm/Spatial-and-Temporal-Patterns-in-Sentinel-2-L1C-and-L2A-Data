import pandas as pd
import os

machine = "laptop"

if machine == "desktop":
    path = "E:/My Drive/School stuff/Geomatics with Remote Sensing and GIS/1st Year/1st Semester/GE7088 Applied Remote Sensing and GIS for Landscape Analysis/Project/Data/Statistical_Data/"
elif machine == "laptop":
    path = "C:/Users/clayz/My Drive/School stuff/Geomatics with Remote Sensing and GIS/1st Year/1st Semester/GE7088 Applied Remote Sensing and GIS for Landscape Analysis/Project/Data/Statistical_Data/"
    
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

Statistical_measures = {'Slope': None, 'Intercept': None, 'Average': None, 'Median': None, 'Skewness': None, 'Kurtosis': None, 'Standard Deviation': None}
keys = list(Statistical_measures.keys())

new_excel_file = os.path.join(path, "All_bands_total.xlsx")
with pd.ExcelWriter(new_excel_file, engine='openpyxl') as writer:
    for i in range(1, 5):
        df_target = pd.DataFrame(columns=keys)
        
        for count_location, point_roi in enumerate(RoIs, start=1):
            location_path = os.path.join(path, f'Location_{count_location}/')
            for count_season, TF in enumerate(Seasons_TF):
                excel_path = os.path.join(location_path, f'Location_{count_location} {Seasons[count_season]}.xlsx')
                
                for n in range(1, 6):
                    r = len(df_target)
                    df_excel = pd.read_excel(excel_path, sheet_name=f'Class_{n}')
                    
                    # Populate `df_target` with values
                    for column_index, column_name in enumerate(keys):
                        cell_value = df_excel.iloc[i - 1, column_index + 1]
                        df_target.loc[r, column_name] = cell_value
        
        # Write each band's data to a new sheet based on the current `i` value
        df_target.to_excel(writer, sheet_name=f"Band_{i}", index=False)
        print(f"Done writing sheet for Band_{i}")

print("Done with all bands")

new_excel_file = os.path.join(path, "All_classes_total.xlsx")
with pd.ExcelWriter(new_excel_file, engine='openpyxl') as writer:
    for n in range(1, 6):
        df_target = pd.DataFrame(columns=keys)
        df_excel = pd.read_excel(excel_path, sheet_name=f'Class_{n}')
        
        for count_location, point_roi in enumerate(RoIs, start=1):
            location_path = os.path.join(path, f'Location_{count_location}/')
            for count_season, TF in enumerate(Seasons_TF):
                excel_path = os.path.join(location_path, f'Location_{count_location} {Seasons[count_season]}.xlsx')
                
                for i in range(1, 5):
                    r = len(df_target)
                    
                    # Populate `df_target` with values
                    for column_index, column_name in enumerate(keys):
                        cell_value = df_excel.iloc[i - 1, column_index + 1]
                        df_target.loc[r, column_name] = cell_value
        
        # Write each band's data to a new sheet based on the current `i` value
        df_target.to_excel(writer, sheet_name=f"Class_{n}", index=False)
        print(f"Done writing sheet for Class_{n}")

print("Done with all bands")


for season in Seasons:
    new_excel_file = os.path.join(path, f"All_bands_{season}.xlsx")
    with pd.ExcelWriter(new_excel_file, engine='openpyxl') as writer:
        for i in range(1, 5):
            df_target = pd.DataFrame(columns=keys)
            
            for count_location, point_roi in enumerate(RoIs, start=1):
                location_path = os.path.join(path, f'Location_{count_location}/')
                excel_path = os.path.join(location_path, f'Location_{count_location} {season}.xlsx')
                
                for n in range(1, 6):
                    r = len(df_target)
                    df_excel = pd.read_excel(excel_path, sheet_name=f'Class_{n}')
                    
                    # Populate `df_target` with values
                    for column_index, column_name in enumerate(keys):
                        cell_value = df_excel.iloc[i - 1, column_index + 1]
                        df_target.loc[r, column_name] = cell_value
            
            # Write each band's data to a new sheet based on the current `i` value
            df_target.to_excel(writer, sheet_name=f"Band_{i}", index=False)
            print(f"Done writing sheet for Band_{i} {season}")

    print(f"Done with all bands for {season}")
            

for season in Seasons:
    new_excel_file = os.path.join(path, f"All_classes_{season}.xlsx")
    with pd.ExcelWriter(new_excel_file, engine='openpyxl') as writer:
        for n in range(1, 6):
            df_target = pd.DataFrame(columns=keys)
            df_excel = pd.read_excel(excel_path, sheet_name=f'Class_{n}')
            
            for count_location, point_roi in enumerate(RoIs, start=1):
                location_path = os.path.join(path, f'Location_{count_location}/')
                excel_path = os.path.join(location_path, f'Location_{count_location} {season}.xlsx')
                
                for i in range(1, 5):
                    r = len(df_target)
                    
                    # Populate `df_target` with values
                    for column_index, column_name in enumerate(keys):
                        cell_value = df_excel.iloc[i - 1, column_index + 1]
                        df_target.loc[r, column_name] = cell_value
            
            # Write each band's data to a new sheet based on the current `i` value
            df_target.to_excel(writer, sheet_name=f"Class_{n}", index=False)
            print(f"Done writing sheet for Class_{n} {season}")

    print(f"Done with all classes for {season}")
            
                    
                    
                    
                
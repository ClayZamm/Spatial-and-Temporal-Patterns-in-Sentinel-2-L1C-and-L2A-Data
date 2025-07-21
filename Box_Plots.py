import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

B_colours = [(0.165, 0.2, 0.75), (0.067, 0.74, 0.031), (0.882, 0.008, 0.008), (0.45, 0.033, 0.033)]
C_colours = [(0.698, 0, 0), (0.926, 0.763, 0.106), (0.156, 0.658, 0.062), (0.090, 0.559, 0.322), (0.107, 0.446, 0.886)]

groups = ['All_bands_Winter', 'All_bands_Spring', 'All_bands_Summer', 'All_bands_Autumn', 'All_bands_total', 'All_classes_Winter', 'All_classes_Spring', 'All_classes_Summer', 'All_classes_Autumn', 'All_classes_total']
stats = ['Slope', 'intercept', 'Average', 'Median', 'Skewness', 'Kurtosis', 'Standard Deviation']

for i, g in enumerate(groups):
    if i < 5:
        lab = 'Bands'
        col_name = ['Band 2', 'Band 3', 'Band 4', 'Band 8']
        sheet_name = 'Band'
        kulur = B_colours
        r = 4
    else:
        lab = 'Classes'
        col_name = ['Class 1', 'Class 2', 'Class 3', 'Class 4', 'Class 5']
        sheet_name = 'Class'
        kulur = C_colours
        r = 5
    for n, s in enumerate(stats):
        df_stats = pd.DataFrame()
        for j in range(r):
            sheet = pd.read_excel(f'C:/Users/clayz/My Drive/School stuff/Geomatics with Remote Sensing and GIS/1st Year/1st Semester/GE7088 Applied Remote Sensing and GIS for Landscape Analysis/Project/Data/Statistical_Data/Statistics 2/{g}.xlsx', sheet_name=f'{sheet_name}_{j+1}')
            col_to_save = sheet.iloc[:, n]
            if n == 2 or n == 6:
                col_to_save = [p / 10000 for p in col_to_save]
            df_stats[f'{col_name[j]}'] = col_to_save
        # with pd.ExcelWriter(f'C:/Users/clayz/My Drive/School stuff/Geomatics with Remote Sensing and GIS/1st Year/1st Semester/GE7088 Applied Remote Sensing and GIS for Landscape Analysis/Project/Data/Statistical_Data/Statistics 2/{g}.xlsx', engine='openpyxl', mode='a') as writer:
        #     df_stats.to_excel(writer, sheet_name=f'{s}', index=False)
            
        df_melted = df_stats.melt(var_name=lab, value_name="Values")
        sns.boxplot(x=lab, y="Values", data=df_melted, palette=kulur)
        if r == 4:
            if n == 0:
                plt.ylim(0, 1.6)
            elif n == 2:
                plt.ylim(0, 0.18)
            elif n == 4:
                plt.ylim(0, 70)
            elif n == 5:
                plt.ylim(0, 9000)
            elif n == 6:
                plt.ylim(0, 0.25)
        elif r == 5:
            if n == 0:
                plt.ylim(0, 1.6)
            elif n == 2:
                plt.ylim(0, 0.10)
            elif n == 4:
                plt.ylim(0, 20)
            elif n == 5:
                plt.ylim(0, 1000)
            elif n == 6:
                plt.ylim(0, 0.05)
        plt.title(f"{s} for {g} box plot")
        os.makedirs(f'C:/Users/clayz/My Drive/School stuff/Geomatics with Remote Sensing and GIS/1st Year/1st Semester/GE7088 Applied Remote Sensing and GIS for Landscape Analysis/Project/Data/Plots/{g}', exist_ok=True)
        plt.savefig(f'C:/Users/clayz/My Drive/School stuff/Geomatics with Remote Sensing and GIS/1st Year/1st Semester/GE7088 Applied Remote Sensing and GIS for Landscape Analysis/Project/Data/Plots/{g}/{s} box_plot for {g}.png', dpi=300, bbox_inches='tight')
        plt.show()
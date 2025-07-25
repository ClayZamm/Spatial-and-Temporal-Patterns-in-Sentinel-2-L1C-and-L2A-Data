# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Define RGB color palettes for plotting: one for band plots, one for class plots
B_colours = [(0.165, 0.2, 0.75), (0.067, 0.74, 0.031), (0.882, 0.008, 0.008), (0.45, 0.033, 0.033)]  # Bands
C_colours = [(0.698, 0, 0), (0.926, 0.763, 0.106), (0.156, 0.658, 0.062), (0.090, 0.559, 0.322), (0.107, 0.446, 0.886)]  # Classes

# Names of grouped Excel files (e.g., by season and type)
groups = [
    'All_bands_Winter', 'All_bands_Spring', 'All_bands_Summer', 'All_bands_Autumn', 'All_bands_total',
    'All_classes_Winter', 'All_classes_Spring', 'All_classes_Summer', 'All_classes_Autumn', 'All_classes_total'
]

# List of statistical measures
stats = ['Slope', 'intercept', 'Average', 'Median', 'Skewness', 'Kurtosis', 'Standard Deviation']

# Loop through each group (bands vs classes)
for i, g in enumerate(groups):
    
    # For the first 5 groups (band-based)
    if i < 5:
        lab = 'Bands'
        col_name = ['Band 2', 'Band 3', 'Band 4', 'Band 8']
        sheet_name = 'Band'
        kulur = B_colours
        r = 4  # Number of bands

    # For the remaining 5 groups (class-based)
    else:
        lab = 'Classes'
        col_name = ['Class 1', 'Class 2', 'Class 3', 'Class 4', 'Class 5']
        sheet_name = 'Class'
        kulur = C_colours
        r = 5  # Number of classes

    # Loop over each statistical measure
    for n, s in enumerate(stats):
        df_stats = pd.DataFrame()

        # Loop through each band/class
        for j in range(r):
            # Read relevant sheet from Excel file
            sheet = pd.read_excel(
                f'C:/Users/clayz/My Drive/.../Statistics 2/{g}.xlsx',
                sheet_name=f'{sheet_name}_{j+1}'
            )
            
            # Extract the column for the current stat
            col_to_save = sheet.iloc[:, n]
            
            # Scale values for 'Average' and 'Standard Deviation'
            if n == 2 or n == 6:  # Index 2: Average, Index 6: Std Dev
                col_to_save = [p / 10000 for p in col_to_save]
            
            # Store column under the respective band/class name
            df_stats[f'{col_name[j]}'] = col_to_save


            with pd.ExcelWriter(...) as writer:
             df_stats.to_excel(writer, sheet_name=f'{s}', index=False)

        # Reshape the DataFrame for seaborn boxplot (long-form)
        df_melted = df_stats.melt(var_name=lab, value_name="Values")

        # Create the boxplot
        sns.boxplot(x=lab, y="Values", data=df_melted, palette=kulur)

        # Adjust y-axis limits based on the stat and whether it's band or class
        if r == 4:  # Bands
            if n == 0: plt.ylim(0, 1.6)
            elif n == 2: plt.ylim(0, 0.18)
            elif n == 4: plt.ylim(0, 70)
            elif n == 5: plt.ylim(0, 9000)
            elif n == 6: plt.ylim(0, 0.25)
        elif r == 5:  # Classes
            if n == 0: plt.ylim(0, 1.6)
            elif n == 2: plt.ylim(0, 0.10)
            elif n == 4: plt.ylim(0, 20)
            elif n == 5: plt.ylim(0, 1000)
            elif n == 6: plt.ylim(0, 0.05)

        # Set title
        plt.title(f"{s} for {g} box plot")

        # Ensure output folder exists
        os.makedirs(f'C:/Users/clayz/My Drive/.../Plots/{g}', exist_ok=True)

        # Save figure to PNG
        plt.savefig(
            f'C:/Users/clayz/My Drive/.../Plots/{g}/{s} box_plot for {g}.png',
            dpi=300, bbox_inches='tight'
        )

        # Show plot
        plt.show()
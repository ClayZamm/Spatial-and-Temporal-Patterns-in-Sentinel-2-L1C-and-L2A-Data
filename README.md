# Sentinel-2 L1C vs L2A Analysis Project

This repository contains a complete pipeline for comparing Sentinel-2 L1C and L2A products across multiple locations and seasons in Sweden. The project covers everything from data acquisition to statistical analysis and visualization.

---

## 📌 Project Objectives

- Download and match Sentinel-2 L1C and L2A scenes using Google Earth Engine
- Extract metadata and surface reflectance values
- Perform regression analysis between L1C and L2A reflectance
- Calculate residual statistics (mean, skewness, etc.)
- Compare results across bands, land use classes, and seasons
- Visualize key statistical differences

---

## 📂 Folder Structure
Sentinel2_L1C_vs_L2A/
│
├── 1_download_data_gee.py
├── 2_check_extent_and_clip.py
├── 3_extract_metadata_json.py
├── 4_bandwise_classwise_regression.py
├── 5_combine_statistics_excel.py
├── 6_plot_boxplots.py
│
├── /Data/
│ ├── Sentinel-2/Location_{n}/{Season}/{L1C, L2A}/
│ ├── Metadata/
│ ├── Statistical_Data/
│ ├── Plots/
│
└── README.md


---

## 🧰 Requirements

- Python 3.8+
- Earth Engine Python API (`earthengine-api`)
- pandas
- geopandas
- rasterio
- openpyxl
- seaborn
- matplotlib
- scikit-learn
- scipy

Install dependencies:
```bash
pip install -r requirements.txt

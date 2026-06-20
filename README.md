# HydroAI
Auditing the freshwater cost of AI
## Note on Raw Data
The raw WRI Aqueduct 4.0 dataset (~200 MB) is not included in this repository due to GitHub's file size limits. To reproduce our cleaning pipeline:

1. Download the Aqueduct 4.0 Current and Future Global Maps Data from 
   [wri.org/data/aqueduct-water-risk-atlas](https://www.wri.org/data/aqueduct-water-risk-atlas)
   (column definitions available at the   [Aqueduct 4.0 Data Dictionary (https://github.com/wri/Aqueduct40/blob/master/data_dictionary_water-risk-atlas.md))
2. Place the file 'Aqueduct40_baseline_annual_y2023m07d05.csv' in 'data/raw/'
3. Run 'notebooks/HydroAI_Week2_DataCleaning.ipynb` to reproduce 'data/processed/aqueduct_water_stress_usa_2023.csv'

The cleaned, filtered version used by HydroAI is already included in 'data/processed/'

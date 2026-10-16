import pandas as pd

file_path = (
    "data/raw/abs_census_sal_vic/"
    "2021_GCP_SAL_for_VIC_short-header/"
    "2021 Census GCP Suburbs and Localities for VIC/"
    "2021Census_G01_VIC_SAL.csv"
)

df = pd.read_csv(file_path)

print("Columns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nShape:")
print(df.shape)
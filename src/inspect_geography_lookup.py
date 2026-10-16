import pandas as pd

file_path = (
    "data/raw/abs_census_sal_vic/"
    "2021_GCP_SAL_for_VIC_short-header/"
    "Metadata/"
    "2021Census_geog_desc_1st_2nd_3rd_release.xlsx"
)

# See all sheet names
excel_file = pd.ExcelFile(file_path)

print("Sheet names:")
print(excel_file.sheet_names)

# Preview each sheet
for sheet in excel_file.sheet_names:

    print("\n" + "=" * 60)
    print("SHEET:", sheet)

    df = pd.read_excel(
        file_path,
        sheet_name=sheet
    )

    print("Columns:")
    print(df.columns.tolist())

    print("\nFirst 5 rows:")
    print(df.head())
import pandas as pd

file_path = (
    "data/raw/abs_census_sal_vic/"
    "2021_GCP_SAL_for_VIC_short-header/"
    "Metadata/"
    "2021Census_geog_desc_1st_2nd_3rd_release.xlsx"
)

excel_file = pd.ExcelFile(file_path)

for sheet in excel_file.sheet_names:

    df = pd.read_excel(
        file_path,
        sheet_name=sheet,
        header=None
    )

    # Convert everything to text
    text_df = df.astype(str)

    # Search for Hawthorn
    hawthorn_mask = text_df.apply(
        lambda row: row.str.contains(
            "Hawthorn",
            case=False,
            na=False
        ).any(),
        axis=1
    )

    if hawthorn_mask.any():

        print("\n" + "=" * 70)
        print("FOUND HAWTHORN IN SHEET:", sheet)

        print(
            df[hawthorn_mask]
            .to_string(index=False)
        )

    # Search for SAL-related rows
    sal_mask = text_df.apply(
        lambda row: row.str.contains(
            "SAL",
            case=False,
            na=False
        ).any(),
        axis=1
    )

    if sal_mask.any():

        print("\n" + "-" * 70)
        print("SAL references in sheet:", sheet)

        print(
            df[sal_mask]
            .head(20)
            .to_string(index=False)
        )
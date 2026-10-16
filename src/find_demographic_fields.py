import pandas as pd
from pathlib import Path

folder = Path(
    "data/raw/abs_census_sal_vic/"
    "2021_GCP_SAL_for_VIC_short-header/"
    "2021 Census GCP Suburbs and Localities for VIC"
)

keywords = [
    "median",
    "income",
    "inc",
    "age",
    "rent",
    "mortgage",
    "household"
]

for file_path in sorted(folder.glob("*.csv")):

    try:
        df = pd.read_csv(
            file_path,
            nrows=2
        )

        matched_columns = []

        for col in df.columns:

            col_lower = col.lower()

            if any(
                keyword in col_lower
                for keyword in keywords
            ):
                matched_columns.append(col)

        if matched_columns:

            print(
                "\nFILE:",
                file_path.name
            )

            for col in matched_columns:
                print("  ", col)

    except Exception as e:
        print(
            "Could not read:",
            file_path.name,
            e
        )
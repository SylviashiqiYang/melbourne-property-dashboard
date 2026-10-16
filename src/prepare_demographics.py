import pandas as pd
from pathlib import Path

base_path = Path(
    "data/raw/abs_census_sal_vic/"
    "2021_GCP_SAL_for_VIC_short-header"
)

g02_file = (
    base_path
    / "2021 Census GCP Suburbs and Localities for VIC"
    / "2021Census_G02_VIC_SAL.csv"
)

lookup_file = (
    base_path
    / "Metadata"
    / "2021Census_geog_desc_1st_2nd_3rd_release.xlsx"
)

# --------------------------------------------------
# Load demographic data
# --------------------------------------------------

g02 = pd.read_csv(g02_file)

demographics = g02[
    [
        "SAL_CODE_2021",
        "Median_age_persons",
        "Median_mortgage_repay_monthly",
        "Median_tot_prsnl_inc_weekly",
        "Median_rent_weekly",
        "Median_tot_fam_inc_weekly",
        "Median_tot_hhd_inc_weekly",
        "Average_household_size"
    ]
].copy()

demographics = demographics.rename(
    columns={
        "SAL_CODE_2021": "sal_code",
        "Median_age_persons": "median_age",
        "Median_mortgage_repay_monthly":
            "median_monthly_mortgage",
        "Median_tot_prsnl_inc_weekly":
            "median_weekly_personal_income",
        "Median_rent_weekly":
            "median_weekly_rent",
        "Median_tot_fam_inc_weekly":
            "median_weekly_family_income",
        "Median_tot_hhd_inc_weekly":
            "median_weekly_household_income",
        "Average_household_size":
            "average_household_size"
    }
)

# --------------------------------------------------
# Load SAL geography lookup
# --------------------------------------------------

lookup_raw = pd.read_excel(
    lookup_file,
    sheet_name="2021_ASGS_Non_ABS_Structures",
    header=None
)

# Based on your search result:
# column 0 = geography type
# column 1 = full geography code
# column 2 = numeric code
# column 3 = geography name
# column 4 = area

sal_lookup = lookup_raw[
    lookup_raw[0] == "SAL"
][
    [1, 3]
].copy()

sal_lookup.columns = [
    "sal_code",
    "suburb"
]

# --------------------------------------------------
# Clean suburb names
# --------------------------------------------------

sal_lookup["suburb"] = (
    sal_lookup["suburb"]
    .astype(str)
    .str.replace(
        r"\s+\(Vic\.\)$",
        "",
        regex=True
    )
    .str.strip()
    .str.title()
)

# --------------------------------------------------
# Merge demographics with suburb names
# --------------------------------------------------

demographics = demographics.merge(
    sal_lookup,
    on="sal_code",
    how="left"
)

# --------------------------------------------------
# Create annual income fields
# --------------------------------------------------

demographics[
    "median_annual_household_income"
] = (
    demographics[
        "median_weekly_household_income"
    ] * 52
)

demographics[
    "median_annual_personal_income"
] = (
    demographics[
        "median_weekly_personal_income"
    ] * 52
)

demographics[
    "median_annual_family_income"
] = (
    demographics[
        "median_weekly_family_income"
    ] * 52
)

# --------------------------------------------------
# Convert metrics to numeric
# --------------------------------------------------

numeric_columns = [
    "median_age",
    "median_monthly_mortgage",
    "median_weekly_personal_income",
    "median_weekly_rent",
    "median_weekly_family_income",
    "median_weekly_household_income",
    "average_household_size",
    "median_annual_household_income",
    "median_annual_personal_income",
    "median_annual_family_income"
]

for col in numeric_columns:
    demographics[col] = pd.to_numeric(
        demographics[col],
        errors="coerce"
    )

# --------------------------------------------------
# Reorder columns
# --------------------------------------------------

demographics = demographics[
    [
        "sal_code",
        "suburb",
        "median_age",
        "median_weekly_personal_income",
        "median_annual_personal_income",
        "median_weekly_family_income",
        "median_annual_family_income",
        "median_weekly_household_income",
        "median_annual_household_income",
        "median_weekly_rent",
        "median_monthly_mortgage",
        "average_household_size"
    ]
]

# --------------------------------------------------
# Save
# --------------------------------------------------

output_file = (
    "data/processed/suburb_demographics.csv"
)

demographics.to_csv(
    output_file,
    index=False
)

print(
    f"Saved successfully to {output_file}"
)

print(
    "\nRows:",
    len(demographics)
)

print(
    "\nMissing suburb names:",
    demographics["suburb"]
    .isna()
    .sum()
)

print(
    "\nHawthorn:"
)

print(
    demographics[
        demographics["suburb"]
        == "Hawthorn"
    ].to_string(index=False)
)
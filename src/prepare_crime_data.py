import pandas as pd


# --------------------------------------------------
# File path
# --------------------------------------------------

path = (
    "data/raw/crime/"
    "Data_Tables_LGA_Recorded_Offences_Year_Ending_June_2026.xlsx"
)


# --------------------------------------------------
# Load Table 02
# --------------------------------------------------

df = pd.read_excel(
    path,
    sheet_name="Table 02"
)


# --------------------------------------------------
# Rename columns
# --------------------------------------------------

df = df.rename(
    columns={
        "Year": "year",
        "Year ending": "year_ending",
        "Police Service Area": "police_service_area",
        "Local Government Area": "lga",
        "Offence Division": "offence_division",
        "Offence Subdivision": "offence_subdivision",
        "Offence Subgroup": "offence_subgroup",
        "Offence Count": "offence_count",
        "LGA Rate per 100,000 population": "lga_rate_per_100k"
    }
)


# --------------------------------------------------
# Clean text
# --------------------------------------------------

text_columns = [
    "lga",
    "offence_division",
    "offence_subdivision",
    "offence_subgroup"
]

for col in text_columns:
    df[col] = (
        df[col]
        .astype(str)
        .str.strip()
    )


# --------------------------------------------------
# Keep latest year ending June 2026
# --------------------------------------------------

df = df[
    (df["year"] == 2026)
    & (df["year_ending"] == "June")
].copy()


# --------------------------------------------------
# Helper function
# --------------------------------------------------

def aggregate_metric(mask):

    result = (
        df[mask]
        .groupby("lga", as_index=False)
        .agg(
            offence_count=(
                "offence_count",
                "sum"
            ),
            offence_rate_per_100k=(
                "lga_rate_per_100k",
                "sum"
            )
        )
    )

    return result


# --------------------------------------------------
# Crimes against the person
# --------------------------------------------------

person_crime = aggregate_metric(
    df["offence_division"].str.startswith(
        "A Crimes against the person",
        na=False
    )
)

person_crime = person_crime.rename(
    columns={
        "offence_count":
            "person_crime_count",
        "offence_rate_per_100k":
            "person_crime_rate_per_100k"
    }
)


# --------------------------------------------------
# Property and deception offences
# --------------------------------------------------

property_crime = aggregate_metric(
    df["offence_division"].str.startswith(
        "B Property and deception offences",
        na=False
    )
)

property_crime = property_crime.rename(
    columns={
        "offence_count":
            "property_crime_count",
        "offence_rate_per_100k":
            "property_crime_rate_per_100k"
    }
)


# --------------------------------------------------
# Burglary
# --------------------------------------------------

burglary = aggregate_metric(
    df["offence_subdivision"].str.contains(
        "Burglary",
        case=False,
        na=False
    )
)

burglary = burglary.rename(
    columns={
        "offence_count":
            "burglary_count",
        "offence_rate_per_100k":
            "burglary_rate_per_100k"
    }
)


# --------------------------------------------------
# Theft
# --------------------------------------------------

theft = aggregate_metric(
    df["offence_subdivision"].str.contains(
        "Theft",
        case=False,
        na=False
    )
)

theft = theft.rename(
    columns={
        "offence_count":
            "theft_count",
        "offence_rate_per_100k":
            "theft_rate_per_100k"
    }
)


# --------------------------------------------------
# Motor vehicle theft
# --------------------------------------------------

motor_vehicle_theft = aggregate_metric(
    df["offence_subgroup"].str.contains(
        "motor vehicle",
        case=False,
        na=False
    )
)

motor_vehicle_theft = (
    motor_vehicle_theft.rename(
        columns={
            "offence_count":
                "motor_vehicle_theft_count",
            "offence_rate_per_100k":
                "motor_vehicle_theft_rate_per_100k"
        }
    )
)


# --------------------------------------------------
# Robbery
# --------------------------------------------------

robbery = aggregate_metric(
    df["offence_subdivision"].str.contains(
        "Robbery",
        case=False,
        na=False
    )
)

robbery = robbery.rename(
    columns={
        "offence_count":
            "robbery_count",
        "offence_rate_per_100k":
            "robbery_rate_per_100k"
    }
)


# --------------------------------------------------
# Sexual offences
# --------------------------------------------------

sexual_offences = aggregate_metric(
    df["offence_subdivision"].str.contains(
        "Sexual offences",
        case=False,
        na=False
    )
)

sexual_offences = sexual_offences.rename(
    columns={
        "offence_count":
            "sexual_offence_count",
        "offence_rate_per_100k":
            "sexual_offence_rate_per_100k"
    }
)


# --------------------------------------------------
# Merge all crime metrics
# --------------------------------------------------

crime_summary = person_crime.merge(
    property_crime,
    on="lga",
    how="outer"
)

crime_summary = crime_summary.merge(
    burglary,
    on="lga",
    how="outer"
)

crime_summary = crime_summary.merge(
    theft,
    on="lga",
    how="outer"
)

crime_summary = crime_summary.merge(
    motor_vehicle_theft,
    on="lga",
    how="outer"
)

crime_summary = crime_summary.merge(
    robbery,
    on="lga",
    how="outer"
)

crime_summary = crime_summary.merge(
    sexual_offences,
    on="lga",
    how="outer"
)


# --------------------------------------------------
# Add year
# --------------------------------------------------

crime_summary["year"] = 2026


# --------------------------------------------------
# Total selected crime count / rate
# --------------------------------------------------

crime_summary["selected_crime_count"] = (
    crime_summary[
        [
            "person_crime_count",
            "property_crime_count"
        ]
    ]
    .sum(
        axis=1,
        skipna=True
    )
)

crime_summary[
    "selected_crime_rate_per_100k"
] = (
    crime_summary[
        [
            "person_crime_rate_per_100k",
            "property_crime_rate_per_100k"
        ]
    ]
    .sum(
        axis=1,
        skipna=True
    )
)


# --------------------------------------------------
# Sort
# --------------------------------------------------

crime_summary = crime_summary.sort_values(
    "selected_crime_rate_per_100k",
    ascending=False
)


# --------------------------------------------------
# Save
# --------------------------------------------------

output_path = (
    "data/processed/lga_crime.csv"
)

crime_summary.to_csv(
    output_path,
    index=False
)


print(
    crime_summary.head(20).to_string()
)

print(
    "\nSaved to:",
    output_path
)
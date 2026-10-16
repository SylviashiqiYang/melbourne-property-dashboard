import geopandas as gpd
import pandas as pd


# --------------------------------------------------
# File paths
# --------------------------------------------------

SUBURB_PATH = (
    "data/processed/victoria_suburbs.geojson"
)

LGA_PATH = (
    "data/raw/lga_boundaries/"
    "VIC_LGA_GDA94/vic_lga.shp"
)

OUTPUT_PATH = (
    "data/processed/suburb_to_lga.csv"
)


# --------------------------------------------------
# Load data
# --------------------------------------------------

print("Loading suburb boundaries...")

suburbs = gpd.read_file(
    SUBURB_PATH
)

print("Loading LGA boundaries...")

lga = gpd.read_file(
    LGA_PATH
)


# --------------------------------------------------
# Show basic information
# --------------------------------------------------

print("\nSuburb CRS:")
print(suburbs.crs)

print("\nLGA CRS:")
print(lga.crs)

print("\nLGA columns:")
print(lga.columns.tolist())


# --------------------------------------------------
# Clean suburb names
# --------------------------------------------------

suburbs["suburb"] = (
    suburbs["suburb"]
    .astype(str)
    .str.strip()
    .str.title()
)


# --------------------------------------------------
# Dissolve duplicate suburb polygons
# --------------------------------------------------

suburbs = (
    suburbs[
        [
            "suburb",
            "geometry"
        ]
    ]
    .dissolve(
        by="suburb"
    )
    .reset_index()
)


# --------------------------------------------------
# Automatically find LGA name column
# --------------------------------------------------

lga_name_column = None

for col in lga.columns:

    if col == "geometry":
        continue

    values = (
        lga[col]
        .dropna()
        .astype(str)
    )

    if values.empty:
        continue

    matches = values.str.contains(
        r"(City|Shire|Rural City|Borough)$",
        case=False,
        regex=True
    )

    if matches.mean() > 0.5:

        lga_name_column = col
        break


if lga_name_column is None:

    raise ValueError(
        "Could not automatically identify "
        "the LGA name column."
    )


print(
    "\nDetected LGA name column:",
    lga_name_column
)


# --------------------------------------------------
# Keep only required LGA fields
# --------------------------------------------------

lga = lga[
    [
        lga_name_column,
        "geometry"
    ]
].copy()

lga = lga.rename(
    columns={
        lga_name_column:
            "lga_full_name"
    }
)


lga["lga_full_name"] = (
    lga["lga_full_name"]
    .astype(str)
    .str.strip()
)


# --------------------------------------------------
# Create crime-compatible LGA name
#
# Crime data uses:
# Boroondara
# Yarra
# Stonnington
#
# Boundary file may use:
# Boroondara City
# Yarra City
# Stonnington City
# --------------------------------------------------

lga["lga"] = (
    lga["lga_full_name"]
    .str.replace(
        r"\s+(City|Shire|Rural City|Borough)$",
        "",
        regex=True
    )
    .str.strip()
)


# --------------------------------------------------
# Convert both datasets to projected CRS
# for area calculations
# --------------------------------------------------

suburbs = suburbs.to_crs(
    epsg=7855
)

lga = lga.to_crs(
    epsg=7855
)


# --------------------------------------------------
# Calculate suburb area
# --------------------------------------------------

suburbs["suburb_area"] = (
    suburbs.geometry.area
)


# --------------------------------------------------
# Spatial intersection
# --------------------------------------------------

print(
    "\nCalculating suburb / LGA intersections..."
)

intersection = gpd.overlay(
    suburbs,
    lga,
    how="intersection",
    keep_geom_type=False
)


# --------------------------------------------------
# Calculate intersection area
# --------------------------------------------------

intersection[
    "intersection_area"
] = (
    intersection.geometry.area
)


intersection[
    "overlap_pct"
] = (
    intersection[
        "intersection_area"
    ]
    / intersection[
        "suburb_area"
    ]
    * 100
)


# --------------------------------------------------
# Pick LGA with largest overlap
# --------------------------------------------------

intersection = (
    intersection
    .sort_values(
        [
            "suburb",
            "intersection_area"
        ],
        ascending=[
            True,
            False
        ]
    )
)


mapping = (
    intersection
    .drop_duplicates(
        subset="suburb",
        keep="first"
    )
    [
        [
            "suburb",
            "lga",
            "lga_full_name",
            "overlap_pct"
        ]
    ]
    .copy()
)


# --------------------------------------------------
# Round overlap percentage
# --------------------------------------------------

mapping[
    "overlap_pct"
] = (
    mapping[
        "overlap_pct"
    ]
    .round(1)
)


# --------------------------------------------------
# Sort
# --------------------------------------------------

mapping = mapping.sort_values(
    "suburb"
)


# --------------------------------------------------
# Save
# --------------------------------------------------

mapping.to_csv(
    OUTPUT_PATH,
    index=False
)


# --------------------------------------------------
# Results
# --------------------------------------------------

print(
    "\nSample mapping:"
)

print(
    mapping.head(30)
    .to_string(
        index=False
    )
)


print(
    "\nSelected Melbourne suburbs:"
)

test_suburbs = [
    "Hawthorn",
    "Hawthorn East",
    "Collingwood",
    "Richmond",
    "South Yarra",
    "Glen Iris",
    "Malvern East",
    "Camberwell",
    "Kew"
]

print(
    mapping[
        mapping[
            "suburb"
        ].isin(
            test_suburbs
        )
    ].to_string(
        index=False
    )
)


print(
    "\nLow-overlap / boundary suburbs:"
)

print(
    mapping[
        mapping[
            "overlap_pct"
        ] < 90
    ]
    .sort_values(
        "overlap_pct"
    )
    .head(30)
    .to_string(
        index=False
    )
)


print(
    "\nSaved to:",
    OUTPUT_PATH
)
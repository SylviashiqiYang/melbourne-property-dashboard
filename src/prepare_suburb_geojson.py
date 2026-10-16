import geopandas as gpd
import pandas as pd

# --------------------------------------------------
# Load suburb boundaries
# --------------------------------------------------

gdf = gpd.read_file(
    "data/raw/locality_polygon/LOCALITY_POLYGON.shp"
)

print("Original CRS:")
print(gdf.crs)

# --------------------------------------------------
# Keep only required columns
# --------------------------------------------------

gdf = gdf[
    [
        "LOCALITY",
        "geometry"
    ]
].copy()

# --------------------------------------------------
# Clean suburb names
# --------------------------------------------------

gdf["suburb"] = (
    gdf["LOCALITY"]
    .astype(str)
    .str.strip()
    .str.title()
)

# --------------------------------------------------
# Convert to latitude / longitude
# --------------------------------------------------

gdf = gdf.to_crs(
    epsg=4326
)

print("\nConverted CRS:")
print(gdf.crs)

# --------------------------------------------------
# Save GeoJSON
# --------------------------------------------------
gdf = gdf[
    [
        "suburb",
        "geometry"
    ]
].dissolve(
    by="suburb"
).reset_index()

gdf[
    [
        "suburb",
        "geometry"
    ]
].to_file(
    "data/processed/victoria_suburbs.geojson",
    driver="GeoJSON"
)

print(
    "\nSaved successfully to "
    "data/processed/victoria_suburbs.geojson"
)

print(
    "\nNumber of suburb polygons:",
    len(gdf)
)


import geopandas as gpd
import pandas as pd
from math import radians, sin, cos, sqrt, atan2

# --------------------------------------------------
# Load suburb polygons
# --------------------------------------------------

gdf = gpd.read_file(
    "data/processed/victoria_suburbs.geojson"
)

# --------------------------------------------------
# Calculate suburb centroid
# --------------------------------------------------

# Reproject to a projected CRS first
gdf_projected = gdf.to_crs(
    epsg=7855
)

gdf_projected["centroid"] = (
    gdf_projected.geometry.centroid
)

# Convert centroid back to lat/lon
centroids = gpd.GeoSeries(
    gdf_projected["centroid"],
    crs=gdf_projected.crs
).to_crs(
    epsg=4326
)

gdf["longitude"] = centroids.x
gdf["latitude"] = centroids.y


# --------------------------------------------------
# Melbourne CBD coordinates
# --------------------------------------------------

CBD_LAT = -37.8136
CBD_LON = 144.9631


# --------------------------------------------------
# Haversine distance
# --------------------------------------------------

def haversine_distance(
    lat1,
    lon1,
    lat2,
    lon2
):

    R = 6371

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        +
        cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return R * c


gdf["distance_to_cbd_km"] = gdf.apply(
    lambda row:
    haversine_distance(
        CBD_LAT,
        CBD_LON,
        row["latitude"],
        row["longitude"]
    ),
    axis=1
)


# --------------------------------------------------
# Save
# --------------------------------------------------

distance_df = gdf[
    [
        "suburb",
        "latitude",
        "longitude",
        "distance_to_cbd_km"
    ]
].copy()

distance_df.to_csv(
    "data/processed/suburb_distance.csv",
    index=False
)

print(
    distance_df
    .sort_values(
        "distance_to_cbd_km"
    )
    .head(30)
)

print(
    "\nSaved to "
    "data/processed/suburb_distance.csv"
)
import geopandas as gpd


INPUT_PATH = (
    "data/processed/victoria_suburbs.geojson"
)

OUTPUT_PATH = (
    "data/processed/victoria_suburbs_simplified.geojson"
)


print("Loading suburb GeoJSON...")

gdf = gpd.read_file(
    INPUT_PATH
)


print("Original CRS:")
print(gdf.crs)


# --------------------------------------------------
# Reproject to metric CRS
# --------------------------------------------------

gdf = gdf.to_crs(
    epsg=7855
)


# --------------------------------------------------
# Simplify geometry
#
# tolerance is in metres because EPSG:7855 is metric
# 20–50m is usually reasonable for suburb polygons
# --------------------------------------------------

print("Simplifying geometry...")

gdf["geometry"] = (
    gdf.geometry.simplify(
        tolerance=30,
        preserve_topology=True
    )
)


# --------------------------------------------------
# Remove invalid / empty geometries
# --------------------------------------------------

gdf = gdf[
    gdf.geometry.notna()
    &
    ~gdf.geometry.is_empty
].copy()


# --------------------------------------------------
# Back to WGS84 for web mapping
# --------------------------------------------------

gdf = gdf.to_crs(
    epsg=4326
)


# --------------------------------------------------
# Save
# --------------------------------------------------

gdf.to_file(
    OUTPUT_PATH,
    driver="GeoJSON"
)


print(
    "\nSaved to:",
    OUTPUT_PATH
)

print(
    "\nRows:",
    len(gdf)
)
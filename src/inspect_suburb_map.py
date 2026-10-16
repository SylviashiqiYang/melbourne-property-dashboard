import geopandas as gpd

gdf = gpd.read_file(
    "data/raw/locality_polygon/LOCALITY_POLYGON.shp"
)

print(gdf.head())
print(gdf.columns)
print(gdf.crs)
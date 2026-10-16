import requests
import json

url = (
    "https://vicmap.land.vic.gov.au/agsgis/rest/services/"
    "vicmap/Vicmap_Admin/MapServer/11/query"
)

params = {
    "where": "1=1",
    "outFields": "locality_name",
    "returnGeometry": "true",
    "f": "geojson",
    "outSR": "4326"
}

response = requests.get(
    url,
    params=params,
    timeout=60
)

response.raise_for_status()

# Check what the server actually returned
data = response.json()

print("Response keys:")
print(data.keys())

# ArcGIS may return an error object instead of GeoJSON
if "error" in data:
    print("\nAPI ERROR:")
    print(json.dumps(data["error"], indent=2))
    raise SystemExit()

if "features" not in data:
    print("\nUnexpected response:")
    print(json.dumps(data, indent=2)[:2000])
    raise SystemExit(
        "\nThe server did not return GeoJSON features."
    )

# Save GeoJSON only after validation
with open(
    "data/raw/victoria_suburbs.geojson",
    "w"
) as f:
    json.dump(
        data,
        f
    )

print(
    "\nSaved successfully to "
    "data/raw/victoria_suburbs.geojson"
)

print(
    "Number of suburbs:",
    len(data["features"])
)
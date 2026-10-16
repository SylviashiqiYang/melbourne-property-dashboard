import pandas as pd

file_path = "data/raw/house_prices.xlsx"

# Load the raw Excel file without assuming a header row
raw = pd.read_excel(
    file_path,
    header=None
)

# --------------------------------------------------
# 1. Find the actual header row
# --------------------------------------------------

header_row = None

for i in range(len(raw)):
    if raw.iloc[i].astype(str).str.contains(
        "Locality",
        case=False,
        na=False
    ).any():
        header_row = i
        break

print("Header row:", header_row)

# Preview the detected header
print(raw.iloc[header_row].to_string())


# --------------------------------------------------
# 2. Identify the suburb column
# --------------------------------------------------

header = raw.iloc[header_row]

suburb_col = header[
    header.astype(str).str.lower() == "locality"
].index[0]

print("Suburb column:", suburb_col)


# --------------------------------------------------
# 3. Detect year columns automatically
# --------------------------------------------------

year_columns = {}

for col in raw.columns:

    value = header[col]

    try:
        year = int(float(value))

        if 2015 <= year <= 2025:
            year_columns[col] = year

    except:
        pass

print("Year columns:")
print(year_columns)


# --------------------------------------------------
# 4. Extract the data section
# --------------------------------------------------

data = raw.iloc[
    header_row + 4:
].copy()

suburb = data[suburb_col]


# --------------------------------------------------
# 5. Convert from wide format to long format
# --------------------------------------------------

records = []

for col, year in year_columns.items():

    temp = pd.DataFrame({
        "suburb": suburb,
        "year": year,
        "median_price": data[col]
    })

    records.append(temp)


house_long = pd.concat(
    records,
    ignore_index=True
)


# --------------------------------------------------
# 6. Clean suburb names
# --------------------------------------------------

house_long["suburb"] = (
    house_long["suburb"]
    .astype(str)
    .str.strip()
    .str.title()
)


# --------------------------------------------------
# 7. Clean median price
# --------------------------------------------------

house_long["median_price"] = pd.to_numeric(
    house_long["median_price"],
    errors="coerce"
)

house_long = house_long.dropna(
    subset=["median_price"]
)


# --------------------------------------------------
# 8. Add property type
# --------------------------------------------------

house_long["property_type"] = "House"


# --------------------------------------------------
# 9. Remove invalid rows
# --------------------------------------------------

house_long = house_long[
    ~house_long["suburb"].isin([
        "Nan",
        "Locality"
    ])
]


# --------------------------------------------------
# 10. Select and sort final columns
# --------------------------------------------------

house_long = house_long[
    [
        "suburb",
        "year",
        "property_type",
        "median_price"
    ]
]

house_long = house_long.sort_values(
    [
        "suburb",
        "year"
    ]
)


# --------------------------------------------------
# 11. Validate the cleaned data
# --------------------------------------------------

print("\nCLEAN DATA:")
print(house_long.head(20))

print("\nNumber of rows:", len(house_long))

print("\nMissing values:")
print(house_long.isna().sum())

print("\nExample - Hawthorn:")
print(
    house_long[
        house_long["suburb"] == "Hawthorn"
    ]
)


# --------------------------------------------------
# 12. Save cleaned data
# --------------------------------------------------

house_long.to_csv(
    "data/processed/house_prices_clean.csv",
    index=False
)

print(
    "\nSaved successfully to "
    "data/processed/house_prices_clean.csv"
)
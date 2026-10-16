import json

import pandas as pd
import plotly.express as px
import streamlit as st


# --------------------------------------------------
# Page config
# --------------------------------------------------

st.set_page_config(
    page_title="Melbourne Property Dashboard",
    layout="wide"
)


# --------------------------------------------------
# Load data
# --------------------------------------------------

price_df = pd.read_csv(
    "data/processed/house_prices_clean.csv"
)

demographics_df = pd.read_csv(
    "data/processed/suburb_demographics.csv"
)

distance_df = pd.read_csv(
    "data/processed/suburb_distance.csv"
)

crime_df = pd.read_csv(
    "data/processed/lga_crime.csv"
)

suburb_lga_df = pd.read_csv(
    "data/processed/suburb_to_lga.csv"
)


with open(
    "data/processed/victoria_suburbs_simplified.geojson",
    "r"
) as f:
    suburbs_geojson = json.load(f)


# --------------------------------------------------
# Clean keys
# --------------------------------------------------

for df in [
    price_df,
    demographics_df,
    distance_df,
    suburb_lga_df
]:
    if "suburb" in df.columns:
        df["suburb"] = (
            df["suburb"]
            .astype(str)
            .str.strip()
            .str.title()
        )


crime_df["lga"] = (
    crime_df["lga"]
    .astype(str)
    .str.strip()
)


suburb_lga_df["lga"] = (
    suburb_lga_df["lga"]
    .astype(str)
    .str.strip()
)


# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("Melbourne Property Dashboard")

st.caption(
    "House prices, demographics, affordability, "
    "distance and crime indicators."
)


# --------------------------------------------------
# Latest year
# --------------------------------------------------

latest_year = int(
    price_df["year"].max()
)


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def calculate_growth(
    suburb,
    years_back
):
    suburb_data = (
        price_df[
            price_df["suburb"] == suburb
        ]
        .sort_values("year")
    )

    latest_row = suburb_data[
        suburb_data["year"] == latest_year
    ]

    past_row = suburb_data[
        suburb_data["year"]
        == latest_year - years_back
    ]

    if (
        latest_row.empty
        or past_row.empty
    ):
        return None

    latest_price = (
        latest_row[
            "median_price"
        ].iloc[0]
    )

    past_price = (
        past_row[
            "median_price"
        ].iloc[0]
    )

    if (
        pd.isna(latest_price)
        or pd.isna(past_price)
        or past_price == 0
    ):
        return None

    return (
        (
            latest_price
            / past_price
        )
        - 1
    ) * 100


def calculate_cagr(
    suburb,
    years_back
):
    suburb_data = (
        price_df[
            price_df["suburb"] == suburb
        ]
        .sort_values("year")
    )

    latest_row = suburb_data[
        suburb_data["year"] == latest_year
    ]

    past_row = suburb_data[
        suburb_data["year"]
        == latest_year - years_back
    ]

    if (
        latest_row.empty
        or past_row.empty
    ):
        return None

    latest_price = (
        latest_row[
            "median_price"
        ].iloc[0]
    )

    past_price = (
        past_row[
            "median_price"
        ].iloc[0]
    )

    if (
        pd.isna(latest_price)
        or pd.isna(past_price)
        or past_price == 0
    ):
        return None

    return (
        (
            latest_price
            / past_price
        )
        ** (1 / years_back)
        - 1
    ) * 100


def format_percent(value):
    if (
        value is None
        or pd.isna(value)
    ):
        return "N/A"

    return f"{value:.1f}%"


def format_currency(value):
    if (
        value is None
        or pd.isna(value)
    ):
        return "N/A"

    return f"${value:,.0f}"


def format_number(value):
    if (
        value is None
        or pd.isna(value)
    ):
        return "N/A"

    return f"{value:,.0f}"


# --------------------------------------------------
# Build latest market dataset
# --------------------------------------------------

latest_market = (
    price_df[
        price_df["year"] == latest_year
    ][
        [
            "suburb",
            "median_price"
        ]
    ]
    .copy()
)


latest_market["growth_1y"] = (
    latest_market["suburb"]
    .apply(
        lambda x:
        calculate_growth(
            x,
            1
        )
    )
)


latest_market["growth_5y"] = (
    latest_market["suburb"]
    .apply(
        lambda x:
        calculate_growth(
            x,
            5
        )
    )
)


latest_market["growth_10y"] = (
    latest_market["suburb"]
    .apply(
        lambda x:
        calculate_growth(
            x,
            10
        )
    )
)


# --------------------------------------------------
# Merge demographics
# --------------------------------------------------

latest_market = latest_market.merge(
    demographics_df,
    on="suburb",
    how="left"
)


# --------------------------------------------------
# Merge distance
# --------------------------------------------------

latest_market = latest_market.merge(
    distance_df,
    on="suburb",
    how="left"
)


# --------------------------------------------------
# Merge suburb -> LGA
# --------------------------------------------------

latest_market = latest_market.merge(
    suburb_lga_df[
        [
            "suburb",
            "lga",
            "lga_full_name",
            "overlap_pct"
        ]
    ],
    on="suburb",
    how="left"
)


# --------------------------------------------------
# Merge crime
# --------------------------------------------------

latest_market = latest_market.merge(
    crime_df,
    on="lga",
    how="left"
)


# --------------------------------------------------
# Derived metrics
# --------------------------------------------------

latest_market["price_to_income"] = (
    latest_market["median_price"]
    / latest_market[
        "median_annual_household_income"
    ]
)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.header("Filters")


available_suburbs = (
    latest_market["suburb"]
    .dropna()
    .sort_values()
    .tolist()
)


default_suburb = (
    "Hawthorn"
    if "Hawthorn"
    in available_suburbs
    else available_suburbs[0]
)


selected_suburb = (
    st.sidebar.selectbox(
        "Select suburb",
        available_suburbs,
        index=available_suburbs.index(
            default_suburb
        )
    )
)


max_budget = (
    st.sidebar.slider(
        "Maximum house budget",
        min_value=300_000,
        max_value=3_000_000,
        value=800_000,
        step=50_000,
        format="$%d"
    )
)


household_income = (
    st.sidebar.number_input(
        "Annual household income",
        min_value=50_000,
        max_value=500_000,
        value=200_000,
        step=10_000
    )
)


max_distance = (
    st.sidebar.slider(
        "Maximum distance from CBD",
        min_value=5,
        max_value=50,
        value=20,
        step=1
    )
)


# --------------------------------------------------
# Income similarity
# --------------------------------------------------

latest_market["income_difference"] = (
    latest_market[
        "median_annual_household_income"
    ]
    - household_income
).abs()


latest_market["income_similarity"] = (
    1
    - (
        latest_market[
            "income_difference"
        ]
        / household_income
    )
) * 100


latest_market["income_similarity"] = (
    latest_market[
        "income_similarity"
    ]
    .clip(
        lower=0,
        upper=100
    )
)


latest_market["income_difference_pct"] = (
    (
        latest_market[
            "median_annual_household_income"
        ]
        - household_income
    )
    / household_income
) * 100


# --------------------------------------------------
# Selected suburb data
# --------------------------------------------------

selected_market = (
    latest_market[
        latest_market["suburb"]
        == selected_suburb
    ]
)


selected_history = (
    price_df[
        price_df["suburb"]
        == selected_suburb
    ]
    .sort_values("year")
)


# --------------------------------------------------
# Selected suburb overview
# --------------------------------------------------

st.header(selected_suburb)


if not selected_market.empty:

    row = selected_market.iloc[0]

    cagr_10y = calculate_cagr(
        selected_suburb,
        10
    )

    col1, col2, col3, col4, col5 = (
        st.columns(5)
    )

    col1.metric(
        f"{latest_year} Median House Price",
        format_currency(
            row["median_price"]
        )
    )

    col2.metric(
        "1Y Growth",
        format_percent(
            row["growth_1y"]
        )
    )

    col3.metric(
        "5Y Growth",
        format_percent(
            row["growth_5y"]
        )
    )

    col4.metric(
        "10Y Growth",
        format_percent(
            row["growth_10y"]
        )
    )

    col5.metric(
        "10Y CAGR",
        format_percent(
            cagr_10y
        )
    )


# --------------------------------------------------
# Suburb profile
# --------------------------------------------------

st.subheader("Suburb Profile")


if not selected_market.empty:

    row = selected_market.iloc[0]

    col1, col2, col3, col4, col5 = (
        st.columns(5)
    )

    col1.metric(
        "Median Household Income",
        format_currency(
            row[
                "median_annual_household_income"
            ]
        )
    )

    col2.metric(
        "Median Age",
        (
            f"{row['median_age']:.0f}"
            if pd.notna(
                row["median_age"]
            )
            else "N/A"
        )
    )

    col3.metric(
        "Median Weekly Rent",
        format_currency(
            row[
                "median_weekly_rent"
            ]
        )
    )

    col4.metric(
        "House Price / Income",
        (
            f"{row['price_to_income']:.1f}x"
            if pd.notna(
                row["price_to_income"]
            )
            else "N/A"
        )
    )

    col5.metric(
        "Distance to CBD",
        (
            f"{row['distance_to_cbd_km']:.1f} km"
            if pd.notna(
                row[
                    "distance_to_cbd_km"
                ]
            )
            else "N/A"
        )
    )


# --------------------------------------------------
# Crime profile
# --------------------------------------------------

st.subheader("Crime Profile")


if not selected_market.empty:

    row = selected_market.iloc[0]

    crime_col1, crime_col2, crime_col3, crime_col4 = (
        st.columns(4)
    )

    crime_col1.metric(
        "Property Crime / 100k",
        format_number(
            row[
                "property_crime_rate_per_100k"
            ]
        )
    )

    crime_col2.metric(
        "Crimes Against Person / 100k",
        format_number(
            row[
                "person_crime_rate_per_100k"
            ]
        )
    )

    crime_col3.metric(
        "Burglary / 100k",
        format_number(
            row[
                "burglary_rate_per_100k"
            ]
        )
    )

    crime_col4.metric(
        "Motor Vehicle Theft / 100k",
        format_number(
            row[
                "motor_vehicle_theft_rate_per_100k"
            ]
        )
    )

    if pd.notna(
        row["lga"]
    ):

        overlap_text = (
            f"{row['overlap_pct']:.1f}%"
            if pd.notna(
                row["overlap_pct"]
            )
            else "N/A"
        )

        st.caption(
            f"Crime data uses {row['lga']} LGA. "
            f"{overlap_text} of {selected_suburb}'s "
            f"geographic area is mapped to this LGA."
        )


# --------------------------------------------------
# Price trend
# --------------------------------------------------

st.subheader("House Price Trend")


fig_trend = px.line(
    selected_history,
    x="year",
    y="median_price",
    markers=True,
    labels={
        "year":
            "Year",

        "median_price":
            "Median House Price"
    }
)


fig_trend.update_layout(
    yaxis_tickprefix="$",
    yaxis_tickformat=","
)


st.plotly_chart(
    fig_trend,
    width="stretch"
)


# --------------------------------------------------
# Map
# --------------------------------------------------

st.header(
    "Melbourne Property Map"
)


# --------------------------------------------------
# Button-style map selector
# --------------------------------------------------

map_view = st.segmented_control(
    "Map View",
    options=[
        "House Price",
        "10-Year Growth",
        "Income Match",
        "Property Crime",
        "Crimes Against Person",
        "Burglary",
        "Motor Vehicle Theft"
    ],
    default="House Price"
)


if map_view is None:
    map_view = "House Price"


# --------------------------------------------------
# Map configuration
# --------------------------------------------------

map_config = {

    "House Price": {
        "column":
            "median_price",

        "label":
            "Median House Price"
    },

    "10-Year Growth": {
        "column":
            "growth_10y",

        "label":
            "10-Year Growth (%)"
    },

    "Income Match": {
        "column":
            "income_similarity",

        "label":
            "Income Similarity (%)"
    },

    "Property Crime": {
        "column":
            "property_crime_rate_per_100k",

        "label":
            "Property Crime Rate / 100k"
    },

    "Crimes Against Person": {
        "column":
            "person_crime_rate_per_100k",

        "label":
            "Crimes Against Person / 100k"
    },

    "Burglary": {
        "column":
            "burglary_rate_per_100k",

        "label":
            "Burglary Rate / 100k"
    },

    "Motor Vehicle Theft": {
        "column":
            "motor_vehicle_theft_rate_per_100k",

        "label":
            "Motor Vehicle Theft / 100k"
    }
}


selected_map = map_config[
    map_view
]


color_column = (
    selected_map[
        "column"
    ]
)


color_label = (
    selected_map[
        "label"
    ]
)


# --------------------------------------------------
# Map data
# --------------------------------------------------

map_df = latest_market.copy()


map_df["suburb_key"] = (
    map_df["suburb"]
    .astype(str)
    .str.strip()
    .str.title()
)


# --------------------------------------------------
# Dynamic hover fields
# --------------------------------------------------

hover_data = {
    "median_price":
        ":$,.0f",

    "growth_10y":
        ":.1f",

    "median_annual_household_income":
        ":$,.0f",

    "distance_to_cbd_km":
        ":.1f",

    "suburb_key":
        False
}


if map_view == "Income Match":

    hover_data[
        "income_similarity"
    ] = ":.1f"

    hover_data[
        "income_difference_pct"
    ] = ":.1f"


if map_view in [
    "Property Crime",
    "Crimes Against Person",
    "Burglary",
    "Motor Vehicle Theft"
]:

    hover_data["lga"] = True

    hover_data[
        "overlap_pct"
    ] = ":.1f"

    hover_data[
        "property_crime_rate_per_100k"
    ] = ":.0f"

    hover_data[
        "person_crime_rate_per_100k"
    ] = ":.0f"

    hover_data[
        "burglary_rate_per_100k"
    ] = ":.0f"

    hover_data[
        "motor_vehicle_theft_rate_per_100k"
    ] = ":.0f"


# --------------------------------------------------
# Map labels
# --------------------------------------------------

map_labels = {
    "median_price":
        "Median House Price",

    "growth_10y":
        "10Y Growth (%)",

    "median_annual_household_income":
        "Median Household Income",

    "income_similarity":
        "Income Similarity (%)",

    "income_difference_pct":
        "Income Difference (%)",

    "distance_to_cbd_km":
        "Distance to CBD (km)",

    "lga":
        "Crime Data LGA",

    "overlap_pct":
        "Suburb in LGA (%)",

    "property_crime_rate_per_100k":
        "Property Crime / 100k",

    "person_crime_rate_per_100k":
        "Crimes Against Person / 100k",

    "burglary_rate_per_100k":
        "Burglary / 100k",

    "motor_vehicle_theft_rate_per_100k":
        "Motor Vehicle Theft / 100k"
}


# --------------------------------------------------
# Create map
# --------------------------------------------------

fig_map = px.choropleth_map(
    map_df,
    geojson=suburbs_geojson,

    locations="suburb_key",

    featureidkey=(
        "properties.suburb"
    ),

    color=color_column,

    hover_name="suburb",

    hover_data=hover_data,

    map_style="carto-positron",

    center={
        "lat":
            -37.8136,

        "lon":
            144.9631
    },

    zoom=9,

    opacity=0.7,

    labels=map_labels
)


fig_map.update_layout(
    margin={
        "r": 0,
        "t": 0,
        "l": 0,
        "b": 0
    },

    coloraxis_colorbar={
        "title":
            color_label
    }
)


st.plotly_chart(
    fig_map,
    width="stretch"
)


# --------------------------------------------------
# Map explanation
# --------------------------------------------------

if map_view == "Income Match":

    st.caption(
        f"Income similarity compares each suburb's "
        f"2021 Census median household income with "
        f"your selected household income of "
        f"${household_income:,.0f}."
    )


if map_view in [
    "Property Crime",
    "Crimes Against Person",
    "Burglary",
    "Motor Vehicle Theft"
]:

    st.caption(
        "Crime statistics are reported at "
        "Local Government Area (LGA) level, "
        "not individual suburb level. "
        "For suburbs spanning multiple LGAs, "
        "the LGA with the largest geographic "
        "overlap is used."
    )


# --------------------------------------------------
# Most expensive suburbs
# --------------------------------------------------

st.header(
    "Most Expensive Suburbs"
)


top_expensive = (
    latest_market[
        latest_market[
            "median_price"
        ].notna()
    ]
    .sort_values(
        "median_price",
        ascending=False
    )
    .head(10)
)


fig_expensive = px.bar(
    top_expensive,

    x="median_price",

    y="suburb",

    orientation="h",

    hover_data={
        "growth_10y":
            ":.1f",

        "median_annual_household_income":
            ":$,.0f",

        "distance_to_cbd_km":
            ":.1f",

        "price_to_income":
            ":.1f"
    },

    labels={
        "median_price":
            "Median House Price",

        "suburb":
            "Suburb"
    }
)


fig_expensive.update_layout(

    yaxis={
        "categoryorder":
            "total ascending"
    },

    xaxis_tickprefix="$",

    xaxis_tickformat=","
)


st.plotly_chart(
    fig_expensive,
    width="stretch"
)


# --------------------------------------------------
# Budget Finder
# --------------------------------------------------

st.header(
    "Budget Finder"
)


budget_match = (
    latest_market[
        (
            latest_market[
                "median_price"
            ]
            <= max_budget
        )
        &
        (
            latest_market[
                "distance_to_cbd_km"
            ]
            <= max_distance
        )
    ]
    .copy()
)


budget_match = (
    budget_match
    .sort_values(
        [
            "distance_to_cbd_km",
            "median_price"
        ]
    )
    .head(20)
)


if budget_match.empty:

    st.info(
        "No suburbs match the current "
        "budget and distance filters."
    )

else:

    fig_budget = px.bar(

        budget_match,

        x="median_price",

        y="suburb",

        orientation="h",

        hover_data={
            "distance_to_cbd_km":
                ":.1f",

            "median_annual_household_income":
                ":$,.0f",

            "growth_10y":
                ":.1f",

            "property_crime_rate_per_100k":
                ":.0f"
        },

        labels={
            "median_price":
                "Median House Price",

            "suburb":
                "Suburb"
        }
    )


    fig_budget.update_layout(

        yaxis={
            "categoryorder":
                "total descending"
        },

        xaxis_tickprefix="$",

        xaxis_tickformat=","
    )


    st.plotly_chart(
        fig_budget,
        width="stretch"
    )


    budget_table = budget_match[
        [
            "suburb",
            "median_price",
            "distance_to_cbd_km",
            "median_annual_household_income",
            "price_to_income",
            "growth_10y",
            "property_crime_rate_per_100k"
        ]
    ].copy()


    budget_table = budget_table.rename(
        columns={
            "suburb":
                "Suburb",

            "median_price":
                "Median Price",

            "distance_to_cbd_km":
                "Distance to CBD (km)",

            "median_annual_household_income":
                "Median Household Income",

            "price_to_income":
                "Price / Income",

            "growth_10y":
                "10Y Growth (%)",

            "property_crime_rate_per_100k":
                "Property Crime / 100k"
        }
    )


    st.dataframe(
        budget_table,
        width="stretch",
        hide_index=True
    )


# --------------------------------------------------
# Income Match
# --------------------------------------------------

st.header(
    "Income Match"
)


income_match_all = (
    latest_market[
        (
            latest_market[
                "median_annual_household_income"
            ]
            .notna()
        )
        &
        (
            latest_market[
                "distance_to_cbd_km"
            ]
            <= max_distance
        )
    ]
    .copy()
)


income_match_top10 = (
    income_match_all
    .sort_values(
        "income_difference"
    )
    .head(10)
)


if income_match_top10.empty:

    st.info(
        "No suburbs match the selected "
        "distance filter."
    )

else:

    fig_income = px.bar(

        income_match_top10,

        x="income_similarity",

        y="suburb",

        orientation="h",

        hover_data={
            "median_annual_household_income":
                ":$,.0f",

            "income_difference_pct":
                ":.1f",

            "median_price":
                ":$,.0f",

            "distance_to_cbd_km":
                ":.1f",

            "growth_10y":
                ":.1f",

            "property_crime_rate_per_100k":
                ":.0f"
        },

        labels={
            "income_similarity":
                "Income Similarity (%)",

            "suburb":
                "Suburb"
        }
    )


    fig_income.update_layout(
        yaxis={
            "categoryorder":
                "total ascending"
        }
    )


    st.plotly_chart(
        fig_income,
        width="stretch"
    )


    income_table = income_match_top10[
        [
            "suburb",
            "median_annual_household_income",
            "income_similarity",
            "income_difference_pct",
            "median_age",
            "median_weekly_rent",
            "distance_to_cbd_km",
            "median_price",
            "growth_10y",
            "property_crime_rate_per_100k"
        ]
    ].copy()


    income_table = income_table.rename(
        columns={
            "suburb":
                "Suburb",

            "median_annual_household_income":
                "Median Household Income",

            "income_similarity":
                "Income Similarity (%)",

            "income_difference_pct":
                "Income Difference (%)",

            "median_age":
                "Median Age",

            "median_weekly_rent":
                "Median Weekly Rent",

            "distance_to_cbd_km":
                "Distance to CBD (km)",

            "median_price":
                "Median House Price",

            "growth_10y":
                "10Y Growth (%)",

            "property_crime_rate_per_100k":
                "Property Crime / 100k"
        }
    )


    st.dataframe(
        income_table,
        width="stretch",
        hide_index=True
    )


# --------------------------------------------------
# Compare suburbs
# --------------------------------------------------

st.header(
    "Compare Suburbs"
)


default_compare = [
    suburb
    for suburb in [
        "Hawthorn",
        "Glen Iris",
        "Collingwood"
    ]
    if suburb in available_suburbs
]


compare_suburbs = st.multiselect(
    "Select up to 5 suburbs",
    options=available_suburbs,
    default=default_compare,
    max_selections=5
)


if compare_suburbs:

    compare_history = (
        price_df[
            price_df[
                "suburb"
            ].isin(
                compare_suburbs
            )
        ]
        .copy()
    )


    fig_compare = px.line(
        compare_history,

        x="year",

        y="median_price",

        color="suburb",

        markers=True,

        labels={
            "year":
                "Year",

            "median_price":
                "Median House Price",

            "suburb":
                "Suburb"
        }
    )


    fig_compare.update_layout(
        yaxis_tickprefix="$",
        yaxis_tickformat=","
    )


    st.plotly_chart(
        fig_compare,
        width="stretch"
    )


    compare_table = (
        latest_market[
            latest_market[
                "suburb"
            ].isin(
                compare_suburbs
            )
        ][
            [
                "suburb",
                "median_price",
                "growth_1y",
                "growth_5y",
                "growth_10y",
                "median_annual_household_income",
                "price_to_income",
                "distance_to_cbd_km",
                "lga",
                "overlap_pct",
                "property_crime_rate_per_100k",
                "person_crime_rate_per_100k",
                "burglary_rate_per_100k",
                "motor_vehicle_theft_rate_per_100k"
            ]
        ]
        .copy()
    )


    compare_table = compare_table.rename(
        columns={
            "suburb":
                "Suburb",

            "median_price":
                "Median Price",

            "growth_1y":
                "1Y Growth (%)",

            "growth_5y":
                "5Y Growth (%)",

            "growth_10y":
                "10Y Growth (%)",

            "median_annual_household_income":
                "Median Household Income",

            "price_to_income":
                "Price / Income",

            "distance_to_cbd_km":
                "Distance to CBD (km)",

            "lga":
                "Crime Data LGA",

            "overlap_pct":
                "Suburb in LGA (%)",

            "property_crime_rate_per_100k":
                "Property Crime / 100k",

            "person_crime_rate_per_100k":
                "Person Crime / 100k",

            "burglary_rate_per_100k":
                "Burglary / 100k",

            "motor_vehicle_theft_rate_per_100k":
                "Vehicle Theft / 100k"
        }
    )


    st.dataframe(
        compare_table,
        width="stretch",
        hide_index=True
    )


# --------------------------------------------------
# Raw data
# --------------------------------------------------

with st.expander(
    "View selected suburb raw price data"
):

    st.dataframe(
        selected_history,
        width="stretch",
        hide_index=True
    )
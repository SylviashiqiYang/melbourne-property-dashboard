import requests
from bs4 import BeautifulSoup
import re

url = (
    "https://www.abs.gov.au/"
    "census/find-census-data/"
    "quickstats/2021/SAL21152"
)

response = requests.get(
    url,
    timeout=30
)

response.raise_for_status()

soup = BeautifulSoup(
    response.text,
    "html.parser"
)

text = soup.get_text(
    " ",
    strip=True
)

print("Page downloaded successfully")

# --------------------------------------------------
# Median age
# --------------------------------------------------

age_match = re.search(
    r"Median age\s+\$?([\d,]+)",
    text
)

if age_match:
    median_age = int(
        age_match.group(1).replace(",", "")
    )
else:
    median_age = None


# --------------------------------------------------
# Median weekly household income
# --------------------------------------------------

income_match = re.search(
    r"Median weekly household income\s+\$([\d,]+)",
    text
)

if income_match:
    median_weekly_income = int(
        income_match.group(1).replace(",", "")
    )
else:
    median_weekly_income = None


print(
    "Median age:",
    median_age
)

print(
    "Median weekly household income:",
    median_weekly_income
)

if median_weekly_income is not None:

    annual_income = (
        median_weekly_income * 52
    )

    print(
        "Median annual household income:",
        annual_income
    )
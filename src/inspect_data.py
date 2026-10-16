import pandas as pd

house = pd.read_excel("data/raw/house_prices.xlsx")

print("HOUSE DATA")
print(house.head(10))
print(house.columns)


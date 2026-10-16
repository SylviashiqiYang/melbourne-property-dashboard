import pandas as pd

file_path = "data/raw/abs_sal_2021.csv"

df = pd.read_csv(file_path)

print(df.columns)
print(df.head())
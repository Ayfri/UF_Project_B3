import pandas as pd

df = pd.read_csv("2022_Nov_2_Events.csv")
print(df.describe())
print(df.head())
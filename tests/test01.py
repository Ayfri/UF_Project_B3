import pandas as pd
import gdelt

gd = gdelt.gdelt(version=1)

# Fetch the GDELT data file for 2012 November 2
results: pd.DataFrame = gd.Search(['2022 Nov 2'], table='gkg', coverage=True)

# save the results to a csv file
results.to_csv('2022_Nov_2_Events.csv')
results.head()
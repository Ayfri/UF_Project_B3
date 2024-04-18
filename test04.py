import pandas as pd
import plotly.express as px
from urllib.request import urlopen
import json

# Load GDELT data
with urlopen('https://api.gdeltproject.org/api/v1/gkg_geojson?QUERY=FOOD_SECURITY') as response:
    gdelt_data = json.load(response)

# Normalize and extract data correctly
df = pd.json_normalize(gdelt_data['features'],
                       meta=[['properties', 'urlpubtimedate'],
                             ['properties', 'name'],
                             ['properties', 'urltone'],
                             ['properties', 'url'],
                             ['properties', 'mentionedthemes']],
                       errors='ignore')

# Add longitude and latitude columns
df['longitude'] = df['geometry.coordinates'].apply(lambda coords: coords[0])
df['latitude'] = df['geometry.coordinates'].apply(lambda coords: coords[1])

# Select and rename columns directly without assigning them all at once to avoid length mismatch error
df = df[['longitude', 'latitude', 'properties.urlpubtimedate', 'properties.name', 'properties.urltone', 'properties.url', 'properties.mentionedthemes']]
df.columns = ['longitude', 'latitude', 'publication_date', 'location_name', 'tone', 'url', 'themes']

# Plot
fig = px.scatter_mapbox(df, lat='latitude', lon='longitude', color='tone',
                        hover_name='location_name', hover_data=['publication_date', 'themes'],
                        color_continuous_scale="Viridis", zoom=3,
                        mapbox_style="carto-positron")
fig.update_layout(margin={"r":0, "t":0, "l":0, "b":0})
fig.show()


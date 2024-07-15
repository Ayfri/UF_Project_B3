import pandas as pd
import plotly.express as px
import json
from urllib.request import urlopen

# Assuming we have internet access and URL resolution works
def fetch_gdelt_data():
    # Fetch the GDELT GeoJSON data
    gdelt_geojson_url = 'https://api.gdeltproject.org/api/v1/gkg_geojson?QUERY=FOOD_SECURITY'
    with urlopen(gdelt_geojson_url) as response:
        gdelt_data = json.load(response)
    return gdelt_data

def fetch_countries_geojson():
    # Fetch the countries GeoJSON file
    with urlopen('https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson') as response:
        countries_geojson = json.load(response)
    return countries_geojson

def prepare_gdelt_dataframe(gdelt_data):
    # Normalize and aggregate the GDELT data
    df = pd.json_normalize(gdelt_data['features'], sep='_')
    df['country_code'] = df['properties_name']  # This needs to be aligned with actual country codes if possible
    df = df.groupby('country_code').properties_urltone.mean().reset_index()
    df.columns = ['country_code', 'average_tone']
    return df

def create_choropleth(df, countries_geojson):
    # Create the choropleth map
    fig = px.choropleth(df,
                        geojson=countries_geojson,
                        locations='country_code',
                        featureidkey='properties.ISO_A3',
                        color='average_tone',
                        color_continuous_scale='Viridis')
    # Update layout options if needed
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0, "t":0, "l":0, "b":0})
    return fig

# Main execution
gdelt_data = fetch_gdelt_data()
countries_geojson = fetch_countries_geojson()
gdelt_df = prepare_gdelt_dataframe(gdelt_data)
choropleth_fig = create_choropleth(gdelt_df, countries_geojson)
choropleth_fig.show()


import numpy as np
import json
from datetime import datetime
from functools import cache

import pandas as pd
from dash import callback, dcc, html, Input, Output, State
from dash.html import Figure

import plotly.express as px
from plotly import graph_objects

from bq.codes import add_event_code_names, event_codes
from bq.queries import get_all_events
from pages.components import header, footer


def create_cartopy_graph(df: pd.DataFrame) -> graph_objects.Figure:
	df['timestamp'] = pd.to_datetime(df['SQLDATE'], format='%Y%m%d', errors='coerce')
	df['formatted-date'] = df['timestamp'].dt.strftime('%d %B %Y')
	df = add_event_code_names(df)

	# Add noise
	noise_level = 0.5
	df['ActionGeo_Lat'] += np.random.uniform(-noise_level, noise_level, size=len(df))
	df['ActionGeo_Long'] += np.random.uniform(-noise_level, noise_level, size=len(df))

	fig = px.scatter_mapbox(
		df,
		lat='ActionGeo_Lat',
		lon='ActionGeo_Long',
		hover_name='Description',
		hover_data={
			'Actor1Name': True,
			'Actor2Name': True,
			'NumArticles': True,
			'GoldsteinScale': True,
			'EventCode': True,
			'formatted-date': True,
		},
		color_continuous_scale=px.colors.diverging.RdYlGn,  # green to red scale
		zoom=2,
		height=900,
		size='NumArticles',
		color='GoldsteinScale',
		range_color=[-10, 10],
		size_max=30,
		mapbox_style="open-street-map",
		labels={
			'ActionGeo_Lat': 'Latitude',
			'ActionGeo_Long': 'Longitude',
			'Actor1Name': 'Acteur 1 Nom',
			'Actor2Name': 'Acteur 2 Nom',
			'EventCode': "Code de l'évènement",
			'GoldsteinScale': 'Échelle de Goldstein',
			'NumArticles': "Nombre d'articles",
			"formatted-date": "Date de l'évènement",
		}
	)
	fig.update_layout(
		mapbox_style="white-bg",
		mapbox_layers=[
			{
				"below": 'traces',
				"sourcetype": "raster",
				"sourceattribution": "United States Geological Survey",
				"source": [
					"https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
				]
			}
		]
	)
	return fig


def simple_map_graph(data = None) -> Figure:
	df = get_all_events(limit=5_000, order='rand()') if data is None else data
	graph = create_cartopy_graph(df)
	return graph


def map_links_graph() -> Figure:
	df = get_all_events(limit=5_000, order='rand()', ActionGeo_Type=1, Actor2Geo_Lat="!=None")
	graph = create_cartopy_graph(df)

	# Collect lat/lon coordinates for lines
	lat_lines = []
	lon_lines = []
	for _, row in df.iterrows():
		lat_lines.extend([row['ActionGeo_Lat'], row['Actor2Geo_Lat'], None])
		lon_lines.extend([row['ActionGeo_Long'], row['Actor2Geo_Long'], None])

	# Add a single trace for all lines
	graph.add_trace(
		graph_objects.Scattermapbox(
			lat=lat_lines,
			lon=lon_lines,
			mode='lines+markers',
			line=graph_objects.scattermapbox.Line(width=1, color='#ffaaaa'),
			showlegend=False,
			opacity=0.4,
			marker=graph_objects.scattermapbox.Marker(size=6, color='#ffffff'),
		)
	)
	return graph


yearly_events_min = 2005
yearly_events_max = 2024


@cache
def get_all_yearly_events() -> pd.DataFrame:
	"""Get all events for the last n years."""
	df = pd.concat([get_all_events(limit=5_000, order='rand()', Year=year) for year in range(yearly_events_min, yearly_events_max + 1)])
	return df


@cache
def get_events_of_year(year: int) -> pd.DataFrame:
	"""Get all events for a specific year."""

	return get_all_yearly_events().query(f'Year == {year}').copy()


@callback(
	Output('world-yearly-content', 'figure'),
	Input('year-selector', 'value'),
)
def simple_map_graph_yearly(year: int = yearly_events_max) -> graph_objects.Figure:
	df = get_events_of_year(year)
	graph = create_cartopy_graph(df)
	return graph


def show_all_years() -> graph_objects.Figure:
	"""Show all years."""
	df = get_all_yearly_events()
	graph = create_cartopy_graph(df)
	return graph


@cache
def get_countries_with_most_events(count: int = 10) -> pd.DataFrame:
	"""Get the countries with the most events."""
	df = get_all_yearly_events()

	# Count the number of events per country code and get the top `count`
	most_events_countries = df['ActionGeo_CountryCode'].value_counts().head(count).reset_index()
	most_events_countries.columns = ['ActionGeo_CountryCode', 'EventCount']

	# Get the first occurrence of each country code with its full name
	country_code_full_name = df[['ActionGeo_CountryCode', 'ActionGeo_FullName']].drop_duplicates('ActionGeo_CountryCode')

	# Merge to add the full name to the top `count` countries
	most_events_countries = most_events_countries.merge(country_code_full_name, on='ActionGeo_CountryCode', how='left')

	return most_events_countries


@cache
def get_events_of_country(country: str) -> pd.DataFrame:
	"""Get all events for a specific country."""
	df = get_all_yearly_events()
	return df.query(f'ActionGeo_CountryCode == "{country}"').copy()


@callback(
	Output('world-country-content', 'figure'),
	Input('country-selector', 'value'),
)
def get_countries_events_graph(country: str) -> graph_objects.Figure:
	"""Get events for a specific country."""
	df = get_events_of_country(country)
	graph = create_cartopy_graph(df)
	graph.update_layout(mapbox={'zoom': 4, 'center': {'lat': df['ActionGeo_Lat'].mean(), 'lon': df['ActionGeo_Long'].mean()}})
	return graph


@callback(
	Output('event-codes-content', 'figure'),
	Input('event-codes-selector', 'value'),
)
def get_event_codes_graph(event_code: str) -> graph_objects.Figure:
	"""Get events for a specific event code."""
	df = get_all_events(limit=5_000, order='rand()', EventCode=event_code)
	graph = create_cartopy_graph(df)
	return graph


content = html.Div(
	id='world-content',
	className='page-content',
	children=[
		html.Div([
			dcc.Markdown(
				"""
				## Évènements mondiaux
				Carte des évènements mondiaux.  
				La taille des points représente le nombre d'articles et la couleur l'échelle de Goldstein.  
				Limites : _5000 events distribuées aléatoirement entre 2000-01-01 et 2024-12-31_
				"""
			),
			dcc.Graph(id='world-content', figure=simple_map_graph()),
		]),
		html.Div([
			dcc.Markdown(
				"""
				## Évènements mondiaux avec liens
				Carte des évènements mondiaux avec les liens entre les acteurs.  
				La taille des points représente le nombre d'articles et la couleur l'échelle de Goldstein.  
				Les lignes représentent les liens entre les acteurs.  
				Limites : _5000 events distribuées aléatoirement entre 2000-01-01 et 2024-12-31_
				"""
			),
			dcc.Graph(id='world-links-content', figure=map_links_graph()),
		]),
		html.Div([
			dcc.Markdown(
				"""
				## Évènements mondiaux par année
				Carte des évènements mondiaux par année.  
				La taille des points représente le nombre d'articles et la couleur l'échelle de Goldstein.  
				Limites : _5000 events distribuées aléatoirement entre YYYY-01-01 et YYYY-12-31_
				"""
			),
			dcc.Graph(id='world-yearly-content'),
			dcc.Slider(
				min=yearly_events_min,
				max=yearly_events_max,
				value=2020,
				step=1,
				updatemode='drag',
				id='year-selector',
				marks={i: str(i) for i in range(yearly_events_min, yearly_events_max + 1)},
			)
		]),
		html.Div(children=[
			dcc.Markdown(
				"""
				## Évènements mondiaux pour toutes les années
				Carte des évènements mondiaux pour toutes les années.  
				La taille des points représente le nombre d'articles et la couleur l'échelle de Goldstein.    
				Limites : _5000 events distribuées aléatoirement entre 2000-01-01 et 2024-12-31_
				"""
			),
			dcc.Graph(id='world-all-years-content', figure=show_all_years()),
		]),
		html.Div(children=[
			dcc.Markdown(
				"""
				## Évènements des 10 pays avec le plus d'évènements
				Carte des évènements des 10 pays avec le plus d'évènements.  
				La taille des points représente le nombre d'articles et la couleur l'échelle de Goldstein.   
				Limites : _5000 events distribuées aléatoirement entre 2000-01-01 et 2024-12-31_
				"""
			),
			dcc.Graph(id='world-country-content'),
			dcc.Dropdown(
				options=[
					{'label': f"{country['ActionGeo_FullName']} ({country['EventCount']})", 'value': country['ActionGeo_CountryCode']}
					for country in get_countries_with_most_events().to_records()
				],
				value='US',
				id='country-selector',
			),
		]),
		html.Div(children=[
			dcc.Markdown(
				"""
				## Évènements pour un code d'évènement
				Carte des évènements pour un code d'évènement.  
				La taille des points représente le nombre d'articles et la couleur l'échelle de Goldstein.    
				Limites : _5000 events distribuées aléatoirement entre 2000-01-01 et 2024-12-31_
				"""
			),
			dcc.Graph(id='event-codes-content'),
			dcc.Dropdown(
				options=[
					{'label': f"{code['Description']} ({code['EventCode']})", 'value': str(code['EventCode'])}
					for code in event_codes.to_records()
				],
				value='010',
				id='event-codes-selector',
			),
		])
	]
)

world_layout = html.Div(
	[
		header('World Page'),
		content,
        footer()
	]
)

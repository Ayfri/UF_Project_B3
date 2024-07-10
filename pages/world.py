from datetime import datetime

import pandas as pd
from dash import dcc, html
from dash.html import Figure

import plotly.express as px
from plotly import graph_objects

from bq.codes import add_event_code_names
from bq.queries import get_all_events
from pages.components import header


def create_cartopy_graph(df: pd.DataFrame)-> graph_objects.Figure:
	df['timestamp'] = pd.to_datetime(df['SQLDATE'], format='%Y%m%d', errors='coerce')
	df['timestamp'].dt.month_name(locale='fr_FR.UTF-8')
	df['formatted-date'] = df['timestamp'].dt.strftime('%d %B %Y')
	df = add_event_code_names(df)

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


def simple_map_graph() -> Figure:
	df = get_all_events(limit=1_000, order='rand()')
	graph = create_cartopy_graph(df)
	return graph


def map_links_graph() -> Figure:
	df = get_all_events(limit=1_000, order='rand()', ActionGeo_Type=1, Actor2Geo_Lat="!=None")
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


content = html.Div([
	dcc.Markdown("""
	## Évènements mondiaux
	Carte des évènements mondiaux.
	La taille des points représente le nombre d'articles et la couleur l'échelle de Goldstein.
	"""),
	dcc.Graph(id='world-content', figure=simple_map_graph()),
	dcc.Markdown("""
	## Évènements mondiaux avec liens
	Carte des évènements mondiaux avec les liens entre les acteurs.
	La taille des points représente le nombre d'articles et la couleur l'échelle de Goldstein.
	Les lignes représentent les liens entre les acteurs.
	"""),
	dcc.Graph(id='world-links-content', figure=map_links_graph()),
])

world_layout = html.Div([
	*header('World Page'),
	content
])

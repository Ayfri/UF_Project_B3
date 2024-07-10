import matplotlib.pyplot as plt
import pandas as pd
from dash import dcc, html
from dash.html import Figure
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.img_tiles import GoogleTiles
from cartopy.mpl.geoaxes import GeoAxes

import plotly.express as px
from bq.queries import get_events
from pages.components import header


def create_cartopy_graph(df: pd.DataFrame) -> Figure:
	# plot a map of the events
	# fig = px.
	# ax: GeoAxes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
	# ax.set_global()
	# ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())
	# ax.coastlines(linestyle='-', color='yellow', linewidth=1.5)
	# ax.add_feature(cfeature.LAND)
	# ax.add_feature(cfeature.OCEAN)
	# ax.add_feature(cfeature.BORDERS, linestyle='-', edgecolor='yellow', linewidth=1.5)
	# ax.add_feature(cfeature.LAKES)
	# ax.add_feature(cfeature.RIVERS)
	# tiler = GoogleTiles(style="satellite", cache=True)
	# ax.add_image(tiler, 4)
	#
	# ax.scatter(
	# 	df['ActionGeo_Long'],
	# 	df['ActionGeo_Lat'],
	# 	transform=ccrs.PlateCarree(),
	# 	color='red',
	# 	marker='.',
	# )
	#

	fig = px.scatter_mapbox(df, lat='ActionGeo_Lat', lon='ActionGeo_Long', hover_name='Actor1Name', zoom=1, height=800, mapbox_style="open-street-map")
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


def map_graph() -> Figure:
	df = pd.DataFrame(get_events(19, year=2020, limit=10_000))
	graph = create_cartopy_graph(df)
	# graph.tight_layout()
	return graph


content = html.Div([
	dcc.Graph(id='world-content', figure=map_graph()),
])

world_layout = html.Div([
	*header('World Page'),
	content
])

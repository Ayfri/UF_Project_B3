import pandas as pd
import plotly.express as px
from dash import callback, dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate

from bq.codes import event_codes
from bq.queries import get_all_events
from pages.components import header

options = {
	'location': 'WORLD',
	'start_time': 2000,
	'end_time': 2024,
	'event_type': 'ALL',
	'feeling_min': -10,
	'feeling_max': 10,
	'limit': 100
}


# Load dropdown values
def _load_location() -> list[str]:
	country_codes_df = pd.read_csv('data/country_codes.csv', header=None)
	country_codes = country_codes_df[0].tolist()
	return country_codes


def _load_event_types() -> list[str]:
	result = [f"{entry['EventCode']} - {entry['Description']}" for entry in event_codes.to_records()]
	return result


def extract_options(options: dict):
	start_date = int(f"{options.get('start_time', 2000)}0101")
	end_date = int(f"{options.get('end_time', 2024)}1231")
	event_type = options.get('event_type', 'ALL')

	# Extract the CAMEO code if the format is "CODE - DESCRIPTION"
	if event_type != 'ALL' and " - " in event_type:
		event_type = event_type.split(" - ")[0]

	return {
		'location': options.get('location', 'WORLD'),
		'start_time': start_date,
		'end_time': end_date,
		'event_type': event_type,
		'feeling_min': float(options.get('feeling_min', -10.0)),
		'feeling_max': float(options.get('feeling_max', 10.0)),
		'limit': options.get('limit', 100)
	}


def prepare_where_clauses(options: dict):
	where_clauses = {
		'Actor1Geo_CountryCode': options['location'] if options['location'] != 'WORLD' else None,
		'SQLDATE>=': options['start_time'],
		'SQLDATE<=': options['end_time'],
		'EventRootCode': options['event_type'] if options['event_type'] != 'ALL' else None,
		'GoldsteinScale>=': options['feeling_min'],
		'GoldsteinScale<=': options['feeling_max'],
	}
	return {k: v for k, v in where_clauses.items() if v is not None}


def create_empty_figure(title: str):
	# Create a minimal DataFrame with a dummy column
	df = pd.DataFrame({'dummy_column': []})
	fig = px.histogram(df, x='dummy_column', title=title)
	fig.update_layout(xaxis_title="Value", yaxis_title="Count")
	return fig


def update_figure_generic(options: dict, x_field: str, y_field: str, chart_type: str):
	where_clauses = prepare_where_clauses(options)
	df = get_all_events(limit=options['limit'], order="rand()", **where_clauses)

	if df.empty:
		return create_empty_figure(f'No data available for the selected criteria: {chart_type}')

	if chart_type == 'bar':
		# Group by country and count the number of events for each country
		df = df.groupby(x_field).size().reset_index(name='NumberOfEvents').sort_values(by='NumberOfEvents', ascending=False).head(20)
		fig = px.bar(df, x=x_field, y='NumberOfEvents', title=f'Number of Events by Country')
	elif chart_type == 'line':
		# Group by year and sum NumArticles for each year
		df['Year'] = df['SQLDATE'].astype(str).str[:4].astype(int)
		df = df.groupby('Year')['NumArticles'].sum().reset_index()
		fig = px.line(df, x='Year', y='NumArticles', title=f'{y_field} by Year')
	elif chart_type == 'scatter':
		fig = px.scatter(df, x=x_field, y=y_field, title=f'{y_field} by {x_field}')
	elif chart_type == 'histogram':
		# Use bin size to improve precision for float values in GoldsteinScale
		fig = px.histogram(df, x=x_field, nbins=50, title=f'{x_field} Distribution')
	else:
		raise ValueError("Unsupported chart type")

	fig.update_layout(xaxis_title=x_field, yaxis_title=y_field)
	return fig


@callback(
	Output('output-container', 'children'),
	Output('options-store', 'data'),
	Output('graph-content-0', 'figure'),
	Output('graph-content-1', 'figure'),
	Output('graph-content-2', 'figure'),
	Output('graph-content-3', 'figure'),
	Input('update-bt', 'n_clicks'),
	State('dropdown-location', 'value'),
	State('input-time-start', 'value'),
	State('input-time-end', 'value'),
	State('dropdown-event', 'value'),
	State('dropdown-feeling-min', 'value'),
	State('dropdown-feeling-max', 'value'),
	State('input-limit', 'value')
)
def update_output(
	n_clicks: int | None,
	location: str,
	start_time: int,
	end_time: int,
	event_type: str,
	feeling_min: str,
	feeling_max: str,
	limit: int
):
	if n_clicks is None or n_clicks == 0:
		raise PreventUpdate

	global options
	options = {
		'location': location,
		'start_time': start_time,
		'end_time': end_time,
		'event_type': event_type,
		'feeling_min': float(feeling_min),
		'feeling_max': float(feeling_max),
		'limit': limit
	}

	extracted_options = extract_options(options)

	fig0 = update_figure_generic(extracted_options, 'Actor1CountryCode', 'NumberOfEvents', 'bar')
	fig1 = update_figure_generic(extracted_options, 'Year', 'NumArticles', 'line')
	fig2 = update_figure_generic(extracted_options, 'GoldsteinScale', 'NumArticles', 'scatter')
	fig3 = update_figure_generic(extracted_options, 'GoldsteinScale', 'Count', 'histogram')

	return f'Button has been clicked {n_clicks} times.', options, fig0, fig1, fig2, fig3


# Components
title = html.H1(children='Dashboard', style={'textAlign': 'center'})
selection_menu = html.Div(
	[
		dcc.Store(id='options-store', data=options),  # Store for options
		html.Div(
			[
				html.Label('Location:'),
				dcc.Dropdown(_load_location(), 'WORLD', id='dropdown-location')
			], style={'margin': '10px'}
		),
		html.Div(
			[
				html.Label('Event Type:'),
				dcc.Dropdown(_load_event_types(), 'ALL - All events', id='dropdown-event')
			], style={'margin': '10px'}
		),
		html.Div(
			[
				html.Label('Start Time:'),
				dcc.Input(id='input-time-start', type='number', value=2000, min=1900, max=2024)
			], style={'margin': '10px'}
		),
		html.Div(
			[
				html.Label('End Time:'),
				dcc.Input(id='input-time-end', type='number', value=2024, min=1900, max=2024)
			], style={'margin': '10px'}
		),
		html.Div(
			[
				html.Label('Min Feeling:'),
				dcc.Input(id='dropdown-feeling-min', type='number', value=-10, min=-10, max=10)
			], style={'margin': '10px'}
		),
		html.Div(
			[
				html.Label('Max Feeling:'),
				dcc.Input(id='dropdown-feeling-max', type='number', value=10, min=-10, max=10)
			], style={'margin': '10px'}
		),
		html.Div(
			[
				html.Label('Limit:'),
				dcc.Input(id='input-limit', type='number', value=1000, min=1)
			], style={'margin': '10px'}
		),
		html.Button('Update', id='update-bt', style={'font-size': '24px'}, n_clicks=0),
		html.Div(id='output-container')
	]
)
fig0 = dcc.Graph(id='graph-content-0', figure=create_empty_figure('Bar Chart'))
fig1 = dcc.Graph(id='graph-content-1', figure=create_empty_figure('Line Chart'))
fig2 = dcc.Graph(id='graph-content-2', figure=create_empty_figure('Scatter Plot'))
fig3 = dcc.Graph(id='graph-content-3', figure=create_empty_figure('Histogram'))

# Content + layout
content = html.Div(
	[
		title,
		selection_menu,
		fig0,
		fig1,
		fig2,
		fig3
	]
)

dashboard_layout = html.Div(
	[
		*header("Dashboard"),
		dcc.Link('World map', '/world'),
		content
	]
)

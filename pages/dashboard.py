import pandas as pd
import plotly.express as px
from dash import callback, dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate

from bq.codes import event_codes
from bq.queries import get_all_events
from pages.components import header, footer

from pages.world import create_cartopy_graph

options = {
    'location': 'WORLD',
    'start_time': '2000-01-01',
    'end_time': '2024-12-31',
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
    start_date = options.get('start_time', '2000-01-01').replace('-', '')
    end_date = options.get('end_time', '2024-12-31').replace('-', '')
    event_type = options.get('event_type', 'ALL')

    # Extract the CAMEO code if the format is "CODE - DESCRIPTION"
    if event_type != 'ALL' and " - " in event_type:
        event_type = event_type.split(" - ")[0]

    return {
        'location': options.get('location', 'WORLD'),
        'start_time': int(start_date),
        'end_time': int(end_date),
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
    elif chart_type == 'box':
        # Filter top 10 countries by number of events and create box plot for GoldsteinScale
        top_countries = df['Actor1CountryCode'].value_counts().head(10).index
        df_top_countries = df[df['Actor1CountryCode'].isin(top_countries)]
        fig = px.box(df_top_countries, x='Actor1CountryCode', y='GoldsteinScale', title='Goldstein Scale by Top 10 Countries')
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
    Output('world-map', 'figure'),
    Input('update-bt', 'n_clicks'),
    State('dropdown-location', 'value'),
    State('input-time-range', 'start_date'),
    State('input-time-range', 'end_date'),
    State('dropdown-event', 'value'),
    State('dropdown-feeling-min', 'value'),
    State('dropdown-feeling-max', 'value'),
    State('input-limit', 'value')
)
def update_output(
    n_clicks: int | None,
    location: str,
    start_time: str,
    end_time: str,
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
    fig2 = update_figure_generic(extracted_options, 'Actor1CountryCode', 'GoldsteinScale', 'box')  # Changed to box plot
    fig3 = update_figure_generic(extracted_options, 'GoldsteinScale', 'Count', 'histogram')

    if "EventRootCode" in extracted_options.keys():
        extracted_options["EventCode"] = extracted_options["EventRootCode"].copy()
        extracted_options.pop("EventRootCode", None)

    where_clauses = prepare_where_clauses(extracted_options)
    df = get_all_events(limit=extracted_options['limit'], order="rand()", **where_clauses)
    map_fig = create_cartopy_graph(df)

    return '', options, fig0, fig1, fig2, fig3, map_fig


# Components
selection_menu = html.Div(
    style={'padding-bottom': '20px'},
    children=[
        dcc.Store(id='options-store', data=options),  # Store for options
        html.H3("Search"),
        html.Div(
            [
                html.Label('Location:'),
                dcc.Dropdown(_load_location(), 'WORLD', id='dropdown-location')
            ]
        ),
        html.Div(
            [
                html.Label('Event Type:'),
                dcc.Dropdown(_load_event_types(), 'ALL - All Events', id='dropdown-event')
            ]
        ),
        html.Div(
            [
                html.Label('Date Range:'),
                dcc.DatePickerRange(
                    id='input-time-range',
                    start_date='2000-01-01',
                    end_date='2024-12-31',
                    display_format='YYYY-MM-DD'
                )
            ],
            className='simple-input'
        ),
        html.Div(
            [
                html.Label('Min Feeling:'),
                dcc.Input(id='dropdown-feeling-min', type='number', value=-10, min=-10, max=10)
            ],
            className='simple-input'
        ),
        html.Div(
            [
                html.Label('Max Feeling:'),
                dcc.Input(id='dropdown-feeling-max', type='number', value=10, min=-10, max=10)
            ],
            className='simple-input'
        ),
        html.Div(
            [
                html.Label('Limit:'),
                dcc.Input(id='input-limit', type='number', value=1000, min=1)
            ],
            className='simple-input'
        ),
        html.Button('Update', id='update-bt', style={'font-size': '24px'}, n_clicks=0),
        html.Div(id='output-container')
    ],
    id="inputs-container"
)

fig0 = dcc.Graph(id='graph-content-0', figure=create_empty_figure('Bar Chart'))
fig1 = dcc.Graph(id='graph-content-1', figure=create_empty_figure('Line Chart'))
fig2 = dcc.Graph(id='graph-content-2', figure=create_empty_figure('Scatter Plot'))
fig3 = dcc.Graph(id='graph-content-3', figure=create_empty_figure('Histogram'))
fig_map = dcc.Graph(id='world-map', figure=create_empty_figure('World Map'))

content = html.Div(
    id='dashboard-content',
    className='page-content',
    children=[
        selection_menu,
        fig0,
        fig1,
        fig2,
        fig3,
        html.Div([
            html.Label('World Map'),
            fig_map,  # Add the map figure to the content
        ])
    ]
)


dashboard_layout = html.Div(
    [
        header("Advanced"),
        content,
        footer()
    ]
)

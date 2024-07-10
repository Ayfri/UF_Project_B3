from dash import html, dcc, Input, Output, callback
from dash.html import Figure
import plotly.express as px
import pandas as pd
import json
import re

from bq.queries import get_all_events, get_events, get_most_fucked_countries, run_query
from pages.components import header

options = {
    'location': 'WORLD',
    'start_time': 1900,
    'end_time': 2023,
    'event_type': 'ALL',
    'feeling_min': -10,
    'feeling_max': 10,
    'limit': 100
}

# Load dropdown values
def _load_location() -> list:
    with open('data/countries.json', 'r') as file:
        country_data = json.load(file)
    
    # Extract country codes
    country_codes = [country['code'] for country in country_data]
    
    # Add "WORLD" and continent names
    locations = ["WORLD", "Africa", "Asia", "Europe", "North America", "Oceania", "South America"] + country_codes
    
    return locations

def _load_time() -> list:
    return list(range(1900, 2024))

def _load_event_types() -> list:
    with open('data/cameo_mapping.json', 'r') as file:
        json_data = json.load(file)

    result = [f"{key} - {value}" for key, value in json_data.items()]

    return ["ALL"] + result

def _load_feelings() -> list:
    return [str(x) for x in range(-10, 11, 1)]

def create_wheres(*, add_where_keyword: bool = False, **where: str | int | float | bool | None) -> str:
    """
    Creates a WHERE clause from a dictionary.
    """
    if not where:
        return ''

    join = ' WHERE ' if add_where_keyword else ' AND '
    conditions = []
    for key, value in where.items():
        match = re.match(r'^(.*?)([<>=!]+)$', key)
        if match:
            field, operator = match.groups()
            if isinstance(value, (int, float)):
                conditions.append(f"{field} {operator} {value}")
            else:
                conditions.append(f"{field} {operator} {repr(value)}")
        else:
            conditions.append(f"{key}={repr(value)}")
    join += ' AND '.join(conditions)
    join = re.sub(r"='!=", "!='", join)
    join = re.sub(r"!='?None'?", " IS NOT NULL", join)
    join = re.sub(r"='?None'?", " IS NULL", join)
    return join

def update_fig_0() -> Figure:
    global options

    # Extract values from the options dictionary
    location = options.get('location', 'WORLD')
    start_time = options.get('start_time', 1900)
    end_time = options.get('end_time', 2023)
    event_type = options.get('event_type', 'ALL')
    feeling_min = options.get('feeling_min', -10.0)
    feeling_max = options.get('feeling_max', 10.0)
    limit = options.get('limit', 100)

    # Prepare the WHERE clause arguments
    where_clauses = {
        'Actor1CountryCode': location if location != 'WORLD' else None,
        'SQLDATE>=': start_time,
        'SQLDATE<=': end_time,
        'EventRootCode': event_type if event_type != 'ALL' else None,
        'GoldsteinScale>=': feeling_min,
        'GoldsteinScale<=': feeling_max,
    }

    # Remove None values from where_clauses
    where_clauses = {k: v for k, v in where_clauses.items() if v is not None}

    # Use get_all_events to get the data
    df = get_all_events(limit=limit, **where_clauses)

    # If DataFrame is empty, return an empty figure
    if df.empty:
        fig = px.bar(title='No data available for the selected criteria')
        fig.update_layout(xaxis_title="CountryCode", yaxis_title="NumberOfConflictsEvents")
        return fig

    # Create the figure
    fig = px.bar(df, x='Actor1CountryCode', y='NumberOfEvents', title='Countries with most conflicts events in the last year')
    fig.update_layout(xaxis_title="CountryCode", yaxis_title="NumberOfConflictsEvents")
    return fig

def update_graph() -> Figure:
    df = pd.DataFrame(get_events(19, year=2020))
    return px.line(df, x='SQLDATE', y='NumArticles', title='Number of Articles per Year')

def update_graph_2() -> Figure:
    df = pd.DataFrame(get_most_fucked_countries(2023, count=10))
    fig = px.bar(df, x='Actor1CountryCode', y='NumberOfEvents', title='Countries with most conflicts events in the last year')
    fig.update_layout(xaxis_title="CountryCode", yaxis_title="NumberOfConflictsEvents")
    return fig

@callback(
    Output('output-container', 'children'),
    Output('options-store', 'data'),
    Input('update-bt', 'n_clicks'),
    Input('dropdown-location', 'value'),
    Input('input-time-start', 'value'),
    Input('input-time-end', 'value'),
    Input('dropdown-event', 'value'),
    Input('dropdown-feeling-min', 'value'),
    Input('dropdown-feeling-max', 'value'),
    Input('input-limit', 'value')
)
def update_output(n_clicks, location, start_time, end_time, event_type, feeling_min, feeling_max, limit):
    global options
    options = {
        'location': location,
        'start_time': start_time,
        'end_time': end_time,
        'event_type': event_type,
        'feeling_min': feeling_min,
        'feeling_max': feeling_max,
        'limit': limit
    }

    if n_clicks is None:
        return 'No updates yet.', options
    return f'Button has been clicked {n_clicks} times.', options

# Components
title = html.H1(children='Title of Dash App', style={'textAlign': 'center'})
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
                html.Label('Start Time:'),
                dcc.Input(id='input-time-start', type='number', value=1900, min=1900, max=2023)
            ], style={'margin': '10px'}
        ),
        html.Div(
            [
                html.Label('End Time:'),
                dcc.Input(id='input-time-end', type='number', value=2023, min=1900, max=2023)
            ], style={'margin': '10px'}
        ),
        html.Div(
            [
                html.Label('Event Type:'),
                dcc.Dropdown(_load_event_types(), 'ALL', id='dropdown-event')
            ], style={'margin': '10px'}
        ),
        html.Div(
            [
                html.Label('Min Feeling:'),
                dcc.Dropdown(_load_feelings(), '-10', id='dropdown-feeling-min')
            ], style={'margin': '10px'}
        ),
        html.Div(
            [
                html.Label('Max Feeling:'),
                dcc.Dropdown(_load_feelings(), '10', id='dropdown-feeling-max')
            ], style={'margin': '10px'}
        ),
        html.Div(
            [
                html.Label('Limit:'),
                dcc.Input(id='input-limit', type='number', value=100, min=1)
            ], style={'margin': '10px'}
        ),
        html.Button('Update', id='update-bt', style={'font-size': '24px'}),
        html.Div(id='output-container')
    ]
)
fig0 = dcc.Graph(id='graph-content', figure=update_fig_0())
fig1 = dcc.Graph(id='graph-content', figure=update_graph())
fig2 = dcc.Graph(id='graph2-content', figure=update_graph_2())

# Content + layout
content = html.Div(
    [
        title,
        selection_menu,
        fig1,
        fig2
    ]
)

dashboard_layout = html.Div(
    [
        *header("Dashboard"),
        dcc.Link('World map', '/world'),
        content
    ]
)
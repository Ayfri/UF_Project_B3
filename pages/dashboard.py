from dash import html, dcc
from dash.html import Figure
import plotly.express as px
import pandas as pd

from bq.queries import get_events, get_most_fucked_countries


def update_graph() -> Figure:
	df = pd.DataFrame(get_events(19, year=2020))
	return px.line(df, x='SQLDATE', y='NumArticles', title='Number of Articles per Year')


def update_graph_2() -> Figure:
    df = pd.DataFrame(get_most_fucked_countries(2023, count=10))
    fig = px.bar(df, x='Actor1CountryCode', y='NumberOfEvents', title='Countries with most conflicts events in the last year')
    fig.update_layout(xaxis_title="CountryCode", yaxis_title="NumberOfConflictsEvents")
    return fig


content = html.Div(
	[
		html.H1(children='Title of Dash App', style={'textAlign': 'center'}),
		dcc.Graph(id='graph-content', figure=update_graph()),
		dcc.Graph(id='graph2-content', figure=update_graph_2())
	]
)



dashboard_layout = html.Div([
    html.H1('Dashboard'),
    dcc.Link('Home', href='/'),
    html.Br(),
    dcc.Link('Dashboard', href='/dashboard'),
    html.Br(),
    dcc.Link('Search', href='/search'),
    html.Br(),
    content
])

from pprint import pprint

from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
from dash.html import Figure

from bq.queries import get_events, get_most_fucked_countries

app = Dash(__name__)


def update_graph() -> Figure:
	# dff = df[df.country == value]
	df = pd.DataFrame(get_events(19, year=2020))
	pprint(df)
	return px.line(df, x='SQLDATE', y='NumArticles', title='Number of Articles per Year')


def update_graph_2() -> Figure:
    df = pd.DataFrame(get_most_fucked_countries(2023, count=10))
    pprint(df)
    fig = px.bar(df, x='Actor1CountryCode', y='NumberOfEvents', title='Countries with most conflicts events in the last year')
    fig.update_layout(xaxis_title="CountryCode", yaxis_title="NumberOfConflictsEvents")
    return fig


app.layout = html.Div(
	[
		html.H1(children='Title of Dash App', style={'textAlign': 'center'}),
		dcc.Graph(id='graph-content', figure=update_graph()),
		dcc.Graph(id='graph2-content', figure=update_graph_2())
	]
)

if __name__ == '__main__':
	app.run(debug=True)

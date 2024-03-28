from pprint import pprint

from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
from dash.html import Figure

from bq.queries import get_events

app = Dash(__name__)


def update_graph() -> Figure:
	# dff = df[df.country == value]
	df = pd.DataFrame(get_events(19, year=2020))
	pprint(df)
	return px.line(df, x='SQLDATE', y='NumArticles', title='Number of Articles per Year')


app.layout = html.Div(
	[
		html.H1(children='Title of Dash App', style={'textAlign': 'center'}),
		dcc.Graph(id='graph-content', figure=update_graph())
	]
)

if __name__ == '__main__':
	app.run(debug=True)

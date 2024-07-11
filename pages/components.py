from dash import dcc, html
from dash.development.base_component import Component

headers = [
	dcc.Link('World Page', href='/'),
	dcc.Link('Advanced Search', href='/advanced'),
]


def header(title: str) -> Component:
	return html.Header(children=[
		html.H1(title),
		html.Nav(children=[
			*headers
		])
	])

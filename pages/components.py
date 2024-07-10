from dash import dcc, html
from dash.development.base_component import Component

headers = [
	dcc.Link('Home', href='/'),
	html.Br(),
	dcc.Link('Dashboard', href='/dashboard'),
	html.Br(),
	dcc.Link('Search', href='/search'),
	html.Br(),
]


def header(title: str) -> list[Component]:
	return [
		html.H1(title),
		*headers
	]

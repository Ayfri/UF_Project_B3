from dash import dcc, html
from dash.development.base_component import Component

headers = [
	dcc.Link('World Page', href='/'),
	html.Br(),
	dcc.Link('Advanced Search', href='/advanced'),
	html.Br(),
]


def header(title: str) -> list[Component]:
	return [
		html.H1(title),
		*headers
	]

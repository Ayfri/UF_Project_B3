from dash import dcc, html
from dash.development.base_component import Component

headers = [
	dcc.Link('World Page', href='/'),
	dcc.Link('Advanced Search', href='/advanced'),
]



def footer() -> Component:
	return html.Footer(children=[
		html.P("Ynov 2023/204 - Bachelore 3 IA Data - Projet UF"),
		html.Br(),
		html.P("ROY Pierre - BORELLO Benjamin")
	])


def header(title: str) -> Component:
	return html.Header(children=[
		html.H1(title),
		html.Nav(children=[
			*headers
		])
	],
	id="header")
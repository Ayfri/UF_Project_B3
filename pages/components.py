from dash import callback, dcc, html, Input, Output
from dash.development.base_component import Component

headers = [
	dcc.Link('World Page', href='/'),
	dcc.Link('Advanced Search', href='/advanced'),
	dcc.Checklist(['Dark Theme'], id='theme-selector', inline=True, className='theme-selector'),
]


@callback(
	Output('theme', 'className'),
	Input('theme-selector', 'value')
)
def theme_callback(value: bool = False) -> str:
	if value:
		return 'dark-theme'
	return 'light-theme'


def footer() -> Component:
	return html.Footer(children=[
		html.P("Ynov 2023/204 - Bachelore 3 IA Data - Projet UF"),
		html.Br(),
		html.P("ROY Pierre - BORELLO Benjamin")
	])


def header(title: str) -> Component:
	return html.Header(
		children=[
			html.Div(id='theme'),
			html.H1(title),
			html.Nav(children=[
				*headers
			])
		],
		id="header"
	)

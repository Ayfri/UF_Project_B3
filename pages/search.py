from dash import html, dcc


search_layout = html.Div([
    html.H1('Search Page'),
    dcc.Link('Home', href='/'),
    html.Br(),
    dcc.Link('Dashboard', href='/dashboard'),
    html.Br(),
    dcc.Link('Search', href='/search')
])

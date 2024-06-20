from dash import html, dcc


home_layout = html.Div([
    html.H1('Home Page'),
    dcc.Link('Home', href='/'),
    html.Br(),
    dcc.Link('Dashboard', href='/dashboard'),
    html.Br(),
    dcc.Link('Search', href='/search')
])


dashboard_layout = html.Div([
    html.H1('Dashboard'),
    dcc.Link('Home', href='/'),
    html.Br(),
    dcc.Link('Dashboard', href='/dashboard'),
    html.Br(),
    dcc.Link('Search', href='/search')
])


search_layout = html.Div([
    html.H1('Search Page'),
    dcc.Link('Home', href='/'),
    html.Br(),
    dcc.Link('Dashboard', href='/dashboard'),
    html.Br(),
    dcc.Link('Search', href='/search')
])

from dash import Dash
from dash import dcc, html, Input, Output
from dash.html import Div

from pages import home, dashboard, search, world

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True)
server = app.server


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname) -> Div:
    if pathname == '/dashboard':
        return dashboard.dashboard_layout
    elif pathname == '/search':
        return search.search_layout
    elif pathname == '/world':
        return world.world_layout
    else:
        return home.home_layout
    

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


if __name__ == '__main__':
    app.run_server(debug=True)

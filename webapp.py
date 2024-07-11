from dash import Dash
from dash import dcc, html, Input, Output
from dash.html import Div

from pages import dashboard, world

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True)
server = app.server


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname) -> Div:
    if pathname == '/advanced':
        return dashboard.dashboard_layout
    else:
        return world.world_layout
    

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


if __name__ == '__main__':
    app.run_server(debug=True)

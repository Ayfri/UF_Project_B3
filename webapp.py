from dash import Dash
from dash import dcc, html, Input, Output

from pages import home, dashboard, search


app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True)
server = app.server


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/dashboard':
        return dashboard.dashboard_layout
    elif pathname == '/search':
        return search.search_layout
    else:
        return home.home_layout
    

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


if __name__ == '__main__':
    app.run_server(debug=True)

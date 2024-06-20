import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Assume app has been defined in app.py and imported here
from app import app
from layouts import layout_home, layout_page1, layout_page2
from pages import dashboard

#    dcc.Location(id='url', refresh=False),
app.layout = html.Div([
    html.Div([
        dcc.Link('Dashboard', href='/'),
        html.Br(),
        dcc.Link('Prediction', href='/predition'),
        html.Br(),
        dcc.Link('Search', href='/search'),
    ]),
    dash.page_container
])

if __name__ == '__main__':
    app.run_server(debug=True)


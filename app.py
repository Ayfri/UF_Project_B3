from dash import Dash


app = Dash(__name__, use_pages=True)
server = app.server  # Expose server for deployments

# Configurations and other setup could be placed here

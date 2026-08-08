from dash import html, dcc
from dashboard.sidebar import create_sidebar

def create_main_layout():
    return html.Div([
        dcc.Location(id="url"),
        dcc.Interval(id="global-interval", interval=5000, n_intervals=0),
        create_sidebar(),
        html.Div(id="page-content", style={"marginLeft": "260px", "padding": "30px", "backgroundColor": "#0f172a", "minHeight": "100vh"})
    ])

import os
import dash
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from dashboard.layout import create_main_layout
from dashboard.pages import executive, voting, voters, candidates, infrastructure, audit, performance
from dashboard.callbacks.executive import register_executive_callbacks
from dashboard.callbacks.voting import register_voting_callbacks
from dashboard.callbacks.voters import register_voter_callbacks
from dashboard.callbacks.candidates import register_candidate_callbacks
from dashboard.callbacks.infrastructure import register_infrastructure_callbacks
from dashboard.callbacks.audit import register_audit_callbacks
from dashboard.callbacks.performance import register_performance_callbacks

# Get dashboard port from .env
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", 8050))

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    ],
    suppress_callback_exceptions=True
)
app.title = "Election Operations Platform"
server = app.server

app.layout = create_main_layout()

# Page Router
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/page-1" or pathname == "/" or pathname is None:
        return executive.layout()
    elif pathname == "/page-2":
        return voting.layout()
    elif pathname == "/page-3":
        return voters.layout()
    elif pathname == "/page-4":
        return candidates.layout()
    elif pathname == "/page-5":
        return infrastructure.layout()
    elif pathname == "/page-6":
        return audit.layout()
    elif pathname == "/page-7":
        return performance.layout()
    return html.Div("404 Not Found", className="text-light")

# Live Timestamp
@app.callback(Output("live-timestamp", "children"), [Input("global-interval", "n_intervals")])
def update_timestamp(n):
    return f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# Register modular callbacks
register_executive_callbacks(app)
register_voting_callbacks(app)
register_voter_callbacks(app)
register_candidate_callbacks(app)
register_infrastructure_callbacks(app)
register_audit_callbacks(app)
register_performance_callbacks(app)

if __name__ == "__main__":
    print(f"?? Starting Dashboard on port {DASHBOARD_PORT}")
    print(f"?? Open: http://localhost:{DASHBOARD_PORT}")
    app.run(debug=True, port=DASHBOARD_PORT)

from dash import html
import dash_bootstrap_components as dbc

def create_sidebar():
    return html.Div(
        [
            html.Div([
                html.H3("ElectionOps", className="text-info fw-bold mb-0"),
                html.P("Enterprise Monitoring", className="text-muted small")
            ], className="p-3 border-bottom border-secondary text-center"),

            dbc.Nav(
                [
                    dbc.NavLink([html.I(className="fa fa-chart-line me-2"), "Executive"], href="/page-1", active="exact", className="text-light"),
                    dbc.NavLink([html.I(className="fa fa-vote-yea me-2"), "Voting"], href="/page-2", active="exact", className="text-light"),
                    dbc.NavLink([html.I(className="fa fa-users me-2"), "Voters"], href="/page-3", active="exact", className="text-light"),
                    dbc.NavLink([html.I(className="fa fa-landmark me-2"), "Candidates"], href="/page-4", active="exact", className="text-light"),
                    dbc.NavLink([html.I(className="fa fa-server me-2"), "Infrastructure"], href="/page-5", active="exact", className="text-light"),
                    dbc.NavLink([html.I(className="fa fa-shield-alt me-2"), "Audit"], href="/page-6", active="exact", className="text-light"),
                    dbc.NavLink([html.I(className="fa fa-tachometer-alt me-2"), "Performance"], href="/page-7", active="exact", className="text-light"),
                ],
                vertical=True,
                pills=True,
                className="p-2"
            ),

            html.Div([
                html.Hr(className="border-secondary"),
                html.Div(id="live-timestamp", className="text-muted small text-center")
            ], className="p-3 mt-auto")
        ],
        style={
            "position": "fixed", "top": 0, "left": 0, "bottom": 0, "width": "260px",
            "backgroundColor": "#111827", "borderRight": "1px solid #374151",
            "display": "flex", "flexDirection": "column", "zIndex": 1000
        }
    )
